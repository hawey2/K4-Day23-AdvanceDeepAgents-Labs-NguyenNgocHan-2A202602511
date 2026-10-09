"""tools.py - STUDENT IMPLEMENTS.  Source tools for the research agents.   Guide: GUIDE.md, part 1.

Rules for every tool:
  * runs on the HOST (not in the sandbox): API keys must never enter the sandbox;
  * returns a STRING (JSON text of compact records) and NEVER raises:
        "NO RESULTS"  when the source answers with nothing,
        "ERROR: ..."  when the source keeps failing after the retries (the agent then tries another source);
  * the docstring is the tool description the LLM reads: keep it precise (what it does, what it returns, when to use it).
Try your tools without any agent:   python tools.py
"""
import json  # noqa: F401
import os  # noqa: F401
import random
import re
import time  # noqa: F401
import xml.etree.ElementTree  # noqa: F401  (arXiv answers with Atom XML)

import httpx  # noqa: F401
from langchain_core.tools import tool

# ---- constants (given) ----
ARXIV_URL = "https://export.arxiv.org/api/query"  # https only: http answers 301
HF_DAILY_URL = "https://huggingface.co/api/daily_papers"
HF_SEARCH_URL = "https://huggingface.co/api/papers/search"
EXA_URL = "https://mcp.exa.ai/mcp"
_last_arxiv_call = 0.0
_RETRY_STATUSES = {429, 500, 502, 503, 504}


def _retry_after(response):
    value = response.headers.get("Retry-After")
    if value is None:
        return None
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        return None


def _request(client, method, url, **kwargs):
    try:
        response = client.request(method, url, **kwargs)
    except httpx.TransportError as exc:
        raise RetryableError(f"{type(exc).__name__}: {exc}") from exc
    if response.status_code in _RETRY_STATUSES:
        raise RetryableError(f"HTTP {response.status_code}", _retry_after(response))
    response.raise_for_status()
    return response


def _has_rate_limit_flag(value):
    if isinstance(value, dict):
        for key, item in value.items():
            label = str(key).lower()
            if any(word in label for word in ("rate", "limit", "throttle")) and item not in (False, None, 0, ""):
                return True
            if _has_rate_limit_flag(item):
                return True
    elif isinstance(value, (list, tuple)):
        return any(_has_rate_limit_flag(item) for item in value)
    elif isinstance(value, str):
        return "rate limit" in value.lower() or "too many requests" in value.lower()
    return False


def _record(item, *, prefer_ai_summary=False):
    paper = item.get("paper") or item
    paper_id = paper.get("id")
    if not paper_id:
        return None
    summary = ((item.get("ai_summary") or paper.get("ai_summary")) if prefer_ai_summary else None) or item.get("summary") or paper.get("summary") or ""
    return {
        "id": str(paper_id),
        "url": f"https://huggingface.co/papers/{paper_id}",
        "published": str(paper.get("publishedAt") or item.get("publishedAt") or "")[:10],
        "title": " ".join(str(item.get("title") or paper.get("title") or "").split()),
        "summary": " ".join(str(summary).split())[:600],
        "upvotes": paper.get("upvotes", 0) or 0,
        "github": paper.get("githubRepo"),
        "stars": paper.get("githubStars", 0) or 0,
    }


def _error(exc, key=None):
    message = f"{type(exc).__name__}: {exc}"
    if key:
        message = message.replace(key, "[REDACTED]")
    return f"ERROR: {message}"


class RetryableError(Exception):
    """Given. Raise it inside a call to ask with_retry to wait and try again (retry_after in seconds, optional)."""

    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after


# ---- TODO 1: retry helper ----
def with_retry(fn, *, attempts=5, base=1.0, cap=30.0):
    """Call fn(); when it raises RetryableError, wait and call it again.

    PSEUDO-CODE:
      for attempt in 0 .. attempts-1:
          try: return fn()
          except RetryableError as e:
              if this was the last attempt: raise
              delay = e.retry_after if the server told us, else exponential backoff base * 2**attempt
              cap the delay at `cap` seconds; add random jitter to the exponential case
              sleep(delay)
    Use it to wrap EVERY network call below. Also treat these as retryable: HTTP 429/500/502/503/504,
    httpx.TransportError (timeouts, connection resets). Read the Retry-After header when present.
    """
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    for attempt in range(attempts):
        try:
            return fn()
        except RetryableError as exc:
            if attempt == attempts - 1:
                raise
            delay = min(cap, exc.retry_after) if exc.retry_after is not None else min(cap, base * (2 ** attempt))
            if exc.retry_after is None:
                delay = min(cap, delay + random.uniform(0, max(0.0, delay * 0.25)))
            time.sleep(delay)


# ---- TODO 2: arXiv ----
@tool
def arxiv_search(query: str, max_results: int = 10) -> str:
    """Search arXiv papers by keywords, newest first. Returns a JSON list of {id, url, published, title, summary}."""
    # PSEUDO-CODE:
    #   keep only word characters of `query` -> terms; no terms -> "NO RESULTS" (do not call the network)
    #   respect arXiv etiquette: at least 3 seconds between two arXiv calls (remember the time of the last call)
    #   GET ARXIV_URL params: search_query="all:t1 AND all:t2 ...", sortBy=submittedDate, sortOrder=descending,
    #       max_results=clamp(max_results, 1, 30)           (wrap in with_retry)
    #   parse the Atom XML: each <entry> -> {id (last part of <id> after /abs/), url, published[:10], title, summary}
    #       collapse whitespace/newlines in title and summary; cut summary to ~600 chars
    #   no entries -> "NO RESULTS"; else json.dumps(records, ensure_ascii=False)
    #   any exception -> "ERROR: <type>: <message>"
    global _last_arxiv_call
    terms = re.findall(r"[A-Za-z0-9]+", query)
    if not terms:
        return "NO RESULTS"
    try:
        params = {"search_query": " AND ".join(f"all:{term}" for term in terms), "sortBy": "submittedDate",
                  "sortOrder": "descending", "max_results": max(1, min(int(max_results), 30)), "start": 0}
        def fetch():
            global _last_arxiv_call
            wait = 3.0 - (time.monotonic() - _last_arxiv_call)
            if _last_arxiv_call and wait > 0:
                time.sleep(wait)
            _last_arxiv_call = time.monotonic()
            with httpx.Client(timeout=30) as client:
                return _request(client, "GET", ARXIV_URL, params=params)
        root = xml.etree.ElementTree.fromstring(with_retry(fetch, attempts=7, cap=60))
        ns = {"a": "http://www.w3.org/2005/Atom"}
        records = []
        for entry in root.findall("a:entry", ns):
            raw_id = (entry.findtext("a:id", default="", namespaces=ns).rsplit("/abs/", 1)[-1])
            paper_id = re.sub(r"v\d+$", "", raw_id)
            if not paper_id:
                continue
            records.append({"id": paper_id, "url": f"https://arxiv.org/abs/{paper_id}",
                            "published": entry.findtext("a:published", default="", namespaces=ns)[:10],
                            "title": " ".join(entry.findtext("a:title", default="", namespaces=ns).split()),
                            "summary": " ".join(entry.findtext("a:summary", default="", namespaces=ns).split())[:600]})
        return json.dumps(records, ensure_ascii=False) if records else "NO RESULTS"
    except Exception as exc:
        return _error(exc)


# ---- TODO 3: Hugging Face ----
@tool
def hf_daily_papers(limit: int = 30, date: str = "", keyword: str = "") -> str:
    """Hugging Face Daily Papers = what is trending in AI research. Returns a JSON list of
    {id, url, published, title, summary, upvotes, github, stars} sorted by upvotes. `date` is YYYY-MM-DD (empty = latest).
    `keyword` filters title/summary; there is no topic search on this endpoint (use hf_search_papers for a topic)."""
    # PSEUDO-CODE:
    #   GET HF_DAILY_URL params: limit (clamp 1..100) and date (only when given)      (with_retry)
    #   response = list of items {"paper": {id, title, summary, upvotes, githubRepo, githubStars, publishedAt}, ...}
    #   map every item to the record shape above (skip items without paper.id); url = https://huggingface.co/papers/<id>
    #   keyword -> keep records whose title+summary contains it (case-insensitive); sort by upvotes descending
    try:
        params = {"limit": max(1, min(int(limit), 100))}
        if date:
            params["date"] = date
        def fetch():
            with httpx.Client(timeout=30) as client:
                return _request(client, "GET", HF_DAILY_URL, params=params)
        items = with_retry(fetch).json()
        records = [_record(item) for item in items]
        records = [r for r in records if r is not None]
        if keyword:
            needle = keyword.casefold()
            records = [r for r in records if needle in (r["title"] + " " + r["summary"]).casefold()]
        records.sort(key=lambda r: r["upvotes"], reverse=True)
        return json.dumps(records, ensure_ascii=False) if records else "NO RESULTS"
    except Exception as exc:
        return _error(exc)


@tool
def hf_search_papers(query: str, limit: int = 10) -> str:
    """Search Hugging Face papers by topic. Returns a JSON list of
    {id, url, published, title, summary, upvotes, github, stars}."""
    # PSEUDO-CODE:
    #   GET HF_SEARCH_URL params: q=query, limit (clamp 1..50)                         (with_retry)
    #   same item shape as the daily endpoint; prefer paper["ai_summary"] over paper["summary"] when present
    try:
        params = {"q": query, "limit": max(1, min(int(limit), 50))}
        def fetch():
            with httpx.Client(timeout=30) as client:
                return _request(client, "GET", HF_SEARCH_URL, params=params)
        items = with_retry(fetch).json()
        records = [_record(item, prefer_ai_summary=True) for item in items]
        records = [r for r in records if r is not None]
        return json.dumps(records, ensure_ascii=False) if records else "NO RESULTS"
    except Exception as exc:
        return _error(exc)


# ---- TODO 4: web search / fetch through the Exa MCP endpoint ----
@tool
def web_search(query: str, objective: str = "", num_results: int = 5) -> str:
    """Search the web (Exa). Describe the ideal page in natural language. Returns clean text of the top results with URLs."""
    # PSEUDO-CODE:
    #   call the MCP tool "web_search_exa" with arguments {query, objective, numResults}
    #       (objective is REQUIRED by Exa: when empty, build one from the query)
    #   see GUIDE.md part 1.4 for how to call an MCP server over plain HTTP (JSON-RPC "tools/call") and read the answer
    #   read optional env EXA_API_KEY; when present it is sent to the Exa endpoint.
    #       (see GUIDE.md 1.4 for where it goes) => the key then appears in exception text: redact it before returning "ERROR: ..."
    #   WATCH OUT: read GUIDE.md 1.4 about how Exa signals "rate limited" on the free tier, and retry on it
    return _exa_call("web_search_exa", {"query": query, "objective": objective or f"Find reliable sources about {query}",
                                         "numResults": max(1, min(int(num_results), 10))})


@tool
def web_fetch(url: str) -> str:
    """Read the full content of one web page (e.g. an arXiv abstract page) as markdown. Long pages are truncated."""
    # PSEUDO-CODE: MCP tool "web_fetch_exa" with arguments {"urls": [url]}; truncate the text to ~12000 chars
    return _exa_call("web_fetch_exa", {"urls": [url]}, truncate=12000)


def _exa_call(name, arguments, truncate=20000):
    key = (os.getenv("EXA_API_KEY") or "").strip()
    endpoint = EXA_URL + ("?" + __import__("urllib.parse", fromlist=["urlencode"]).urlencode({"exaApiKey": key}) if key else "")
    payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}}
    try:
        def fetch():
            with httpx.Client(timeout=60) as client:
                response = _request(client, "POST", endpoint, json=payload,
                                    headers={"Accept": "application/json, text/event-stream"})
            text = response.text
            data = None
            for line in text.splitlines():
                if line.startswith("data:"):
                    data = json.loads(line[5:].strip())
                    break
            if data is None:
                try:
                    data = response.json()
                except ValueError:
                    raise ValueError("Exa returned no JSON-RPC response")
            if data.get("error"):
                raise ValueError(str(data["error"]))
            result = data.get("result") or {}
            meta = result.get("_meta") or {}
            content = "\n".join(part.get("text", "") for part in result.get("content", []) if part.get("type") == "text")
            if _has_rate_limit_flag(meta) or "rate limit" in content.lower() or "too many requests" in content.lower():
                raise RetryableError("Exa rate limit", 20)
            return content[:truncate] if content else "NO RESULTS"
        return with_retry(fetch, attempts=8, base=2, cap=60)
    except Exception as exc:
        return _error(exc, key)


# ---- TODO 5: registry (the researcher subagent gets exactly these) ----
SOURCE_TOOLS = [arxiv_search, hf_daily_papers, hf_search_papers, web_search, web_fetch]


if __name__ == "__main__":
    for name, fn, args in [
        ("arxiv_search", arxiv_search, {"query": "world model", "max_results": 3}),
        ("hf_daily_papers", hf_daily_papers, {"limit": 20}),
        ("hf_search_papers", hf_search_papers, {"query": "world model", "limit": 3}),
        ("web_search", web_search, {"query": "survey paper on world models", "num_results": 2}),
        ("web_fetch", web_fetch, {"url": "https://arxiv.org/abs/1803.10122"}),
    ]:
        try:
            print(f"== {name}\n{fn.invoke(args)[:400]}\n")
        except NotImplementedError as exc:
            print(f"== {name}: not implemented yet ({exc})\n")
