"""research.py - STUDENT IMPLEMENTS.  The main script.   Guide: GUIDE.md, part 3.

Usage:  python research.py "survey about world model"
Result: reports/<slug>.md   reports/<slug>.sources.json   reports/<slug>.meta.json
"""
import json  # noqa: F401
import os  # noqa: F401
import re  # noqa: F401
import sys
import time  # noqa: F401
from collections import Counter  # noqa: F401
from pathlib import Path

from agents import FINALIZER_PATH, REPORT_PATH, SOURCES_PATH, VALIDATOR_PATH, WORKDIR, build_lead_agent  # noqa: F401
from model import make_model  # noqa: F401
from sandbox import download, open_sandbox, upload  # noqa: F401

ROOT = Path(__file__).parent
REPORTS = ROOT / "reports"
VALIDATOR_SOURCE = ROOT / "check_citations.py"
FINALIZER_SOURCE = ROOT / "finalize_citations.py"   # provided: uploaded next to your validator


def slugify(topic):
    """Turn a topic into a safe file name: lower case, runs of non-word characters become one "-", max 60 chars,
    never empty (fall back to "topic"). The topic is user input: "../../x" must not escape reports/."""
    slug = re.sub(r"\W+", "-", str(topic).lower(), flags=re.UNICODE).strip("-")[:60].strip("-")
    return slug or "topic"


def build_prompt(topic):
    """The user message sent to the lead agent."""
    return (f"Research this topic: {topic}\n\nPlan with write_todos and delegate at least three independent sub-questions "
            "in parallel. For every researcher delegation include this topic, the exact sub-question, at least two "
            "requested source families, the absolute note path under /tmp/work/research/notes/, and the required note "
            "format from your system instructions. Check returned notes before synthesis.")


def summarize(messages, elapsed, model_name):
    """Return {"model", "elapsed_s", "subagent_calls", "tool_calls": {name: count}, "tokens": {"input", "output"}}.

    PSEUDO-CODE: walk the lead's messages; for every message with tool_calls count call["name"] (subagent_calls = the
    count of "task"); add the input/output token counts from each message's usage_metadata when present.
    (Lead messages only: subagent tokens are not included, so this undercounts the real cost.)
    elapsed_s rounded to 0.1.
    """
    tool_calls, tokens, subagent_calls = Counter(), {"input": 0, "output": 0}, 0
    for message in messages or []:
        calls = getattr(message, "tool_calls", None) or []
        for call in calls:
            name = call.get("name") if isinstance(call, dict) else getattr(call, "name", None)
            if name:
                tool_calls[name] += 1
                subagent_calls += name == "task"
        usage = getattr(message, "usage_metadata", None) or {}
        if isinstance(usage, dict):
            tokens["input"] += usage.get("input_tokens", 0) or 0
            tokens["output"] += usage.get("output_tokens", 0) or 0
    return {"model": model_name, "elapsed_s": round(elapsed, 1), "subagent_calls": subagent_calls,
            "tool_calls": dict(tool_calls), "tokens": tokens}


def save_outputs(backend, topic, messages, elapsed, model_name, reports_dir=REPORTS):
    """Download the report from the sandbox and write the three files into reports_dir. Return the report path.

    PSEUDO-CODE:
      files = download(backend, [REPORT_PATH, SOURCES_PATH])
      if the report is missing/empty or sources.json is missing/invalid JSON: raise RuntimeError and WRITE NOTHING
          (a failed run must never leave an empty or half-written report behind)
      write <slug>.sources.json, <slug>.meta.json (topic + summarize(...) + n_sources + source_families: the sorted
      distinct "source" values of sources.json) and <slug>.md
    """
    files = download(backend, [REPORT_PATH, SOURCES_PATH])
    report_bytes, sources_bytes = files.get(REPORT_PATH), files.get(SOURCES_PATH)
    if not report_bytes or not sources_bytes:
        raise RuntimeError("sandbox did not produce a non-empty report and sources.json")
    try:
        report = report_bytes.decode("utf-8")
        sources = json.loads(sources_bytes.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise RuntimeError(f"invalid sandbox output: {exc}") from exc
    if not report.strip() or not isinstance(sources, list) or not sources or not all(isinstance(s, dict) for s in sources):
        raise RuntimeError("report is empty or sources.json is not a non-empty list of objects")
    families = sorted({s.get("source") for s in sources if isinstance(s.get("source"), str)})
    metadata = {"topic": topic, **summarize(messages, elapsed, model_name), "n_sources": len(sources),
                "source_families": families}
    stem = slugify(topic)
    paths = [reports_dir / f"{stem}.md", reports_dir / f"{stem}.sources.json", reports_dir / f"{stem}.meta.json"]
    contents = [report, json.dumps(sources, ensure_ascii=False, indent=2) + "\n",
                json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"]
    reports_dir.mkdir(parents=True, exist_ok=True)
    # Stage all outputs first; only replace final files once every stage was written.
    staged = []
    try:
        for path, content in zip(paths, contents):
            temp = path.with_name(path.name + ".tmp")
            temp.write_text(content, encoding="utf-8")
            staged.append((temp, path))
        for temp, path in staged:
            temp.replace(path)
    finally:
        for temp, _ in staged:
            temp.unlink(missing_ok=True)
    return paths[0]


def main(topic):
    """Return the process exit code (0 ok, 1 failed run, 2 no topic).

    PSEUDO-CODE:
      empty topic -> print usage to stderr, return 2
      model = make_model(); start = time.monotonic()
      with open_sandbox() as backend:                # the sandbox is always cleaned up, even on errors
          backend.execute("mkdir -p <WORKDIR>/research/notes <WORKDIR>/report")
          upload(backend, {VALIDATOR_PATH: VALIDATOR_SOURCE.read_bytes(), FINALIZER_PATH: FINALIZER_SOURCE.read_bytes()})
          agent = build_lead_agent(backend, model)
          result = agent.invoke({"messages": [{"role": "user", "content": build_prompt(topic)}]},
                                config={"recursion_limit": 1000})
          save_outputs(...); on RuntimeError print "FAILED: ..." to stderr and return 1
      print where the report was saved; return 0
    """
    if not topic.strip():
        print('Usage: python research.py "<topic>"', file=sys.stderr)
        return 2
    try:
        model = make_model()
        model_name = os.getenv("LAB_MODEL") or os.getenv("OPENAI_DEPLOYMENT_MODEL") or type(model).__name__
        start = time.monotonic()
        with open_sandbox() as backend:
            backend.execute(f"mkdir -p {WORKDIR}/research/notes {WORKDIR}/report")
            upload(backend, {VALIDATOR_PATH: VALIDATOR_SOURCE.read_bytes(), FINALIZER_PATH: FINALIZER_SOURCE.read_bytes()})
            agent = build_lead_agent(backend, model)
            result = agent.invoke({"messages": [{"role": "user", "content": build_prompt(topic)}]},
                                  config={"recursion_limit": 1000})
            elapsed = time.monotonic() - start
            messages = result.get("messages", []) if isinstance(result, dict) else []
            report_path = save_outputs(backend, topic, messages, elapsed, model_name)
        print(f"Saved report: {report_path}")
        return 0
    except Exception as exc:
        print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(" ".join(sys.argv[1:])))
