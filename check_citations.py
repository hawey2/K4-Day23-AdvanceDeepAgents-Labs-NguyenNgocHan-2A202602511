"""check_citations.py - STUDENT IMPLEMENTS `check`.   Runs INSIDE the sandbox (standard library only).

research.py uploads this file to the sandbox and the lead agent runs it with the `execute` tool:
    python3 /tmp/work/research/check_citations.py [report.md] [sources.json]
It must exit 0 and print "OK: ..." when the report is consistent, else print each problem and exit 1.
"""
import json
import re
import sys

REPORT = "/tmp/work/report/report.md"
SOURCES = "/tmp/work/research/sources.json"


def check(report_text, sources):
    """Return a list of problem strings (empty list = OK).

    PSEUDO-CODE:
      problems = []
      if sources is empty: return ["no sources in sources.json"]
      for each source entry:
          n must be an int                       -> problem if not
          url must start with http:// or https://-> problem if not
          the same url must not appear twice     -> problem if duplicated
      split report_text at the heading "## References":
          body = text before it; if the heading is missing -> problem
      cited = set of numbers found as [n] in the BODY only (not in the reference list; use a regex)
      every number in `cited` must exist in sources -> problem "[n] cited but missing from sources.json"
      every source number must be in `cited`        -> problem "source [n] never cited"
      the lines of the References section that start with "[n]" (regex) are the reference lines:
          every source needs exactly ONE reference line (none missing, no number twice, no number that is not a source)
          each reference line holds exactly ONE http(s) URL and it must equal that source's url
          (a line bundling several sources under one number is a problem)
      return problems
    """
    problems = []
    if not isinstance(sources, list) or not sources:
        return ["no sources in sources.json"]
    by_number = {}
    seen_urls = set()
    for source in sources:
        if not isinstance(source, dict):
            problems.append("source entry must be an object")
            continue
        number, url = source.get("n"), source.get("url")
        if not isinstance(number, int) or isinstance(number, bool):
            problems.append(f"source number {number!r} is not an integer")
        elif number in by_number:
            problems.append(f"duplicate source number [{number}]")
        else:
            by_number[number] = source
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            problems.append(f"source [{number}] has invalid URL")
        elif url in seen_urls:
            problems.append(f"duplicate source URL: {url}")
        else:
            seen_urls.add(url)

    headings = list(re.finditer(r"(?m)^##[ \t]+References[ \t]*$", report_text))
    if not headings:
        return problems + ["missing ## References heading"]
    body = report_text[:headings[-1].start()]
    references = report_text[headings[-1].end():]
    # Ignore inline/fenced code and Markdown links, which are not citations.
    body = re.sub(r"```.*?```|`[^`\n]*`", "", body, flags=re.DOTALL)
    body = re.sub(r"\[(\d+)\]\([^)]*\)", "", body)
    cited = {int(n) for n in re.findall(r"\[(\d+)\]", body)}
    for number in sorted(cited - set(by_number)):
        problems.append(f"[{number}] cited but missing from sources.json")
    for number in sorted(set(by_number) - cited):
        problems.append(f"source [{number}] never cited")

    ref_lines = [line for line in references.splitlines() if re.match(r"^\s*\[\d+\]", line)]
    refs_by_number = {}
    for line in ref_lines:
        match = re.match(r"^\s*\[(\d+)\]", line)
        number = int(match.group(1))
        refs_by_number.setdefault(number, []).append(line)
    for number in by_number:
        count = len(refs_by_number.get(number, []))
        if count == 0:
            problems.append(f"missing reference line for [{number}]")
        elif count > 1:
            problems.append(f"duplicate reference line for [{number}]")
        elif len(re.findall(r"https?://\S+", refs_by_number[number][0])) != 1:
            problems.append(f"reference [{number}] must contain exactly one URL")
        elif re.findall(r"https?://\S+", refs_by_number[number][0])[0].rstrip(".,;>") != by_number[number].get("url"):
            problems.append(f"reference [{number}] URL does not match sources.json")
    for number in sorted(set(refs_by_number) - set(by_number)):
        problems.append(f"reference [{number}] has no source")
    return problems


def main(argv):
    report_path = argv[1] if len(argv) > 1 else REPORT
    sources_path = argv[2] if len(argv) > 2 else SOURCES
    try:
        with open(report_path, encoding="utf-8") as f:
            report = f.read()
        with open(sources_path, encoding="utf-8") as f:
            sources = json.load(f)
    except (OSError, ValueError) as exc:
        print(f"cannot read inputs: {exc}")
        return 1
    problems = check(report, sources)
    if problems:
        print("\n".join(problems))
        return 1
    print(f"OK: {len(sources)} sources, all citations resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
