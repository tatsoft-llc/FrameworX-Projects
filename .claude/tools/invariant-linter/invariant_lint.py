#!/usr/bin/env python
"""
FrameworX-Projects invariant linter: read-only structural drift check.

WHY THIS EXISTS
    This workspace guards several structural invariants by PROSE + HUMAN
    DISCIPLINE only (CLAUDE.md, KnowledgeBase/Conventions/*). Prose drifts
    silently. The per-solution test harness (.claude/skills/run-tests/check.py)
    is runtime-dependent and per-project; it does NOT cover repo-level
    structure. This linter is the cheap deterministic guard for the rules a
    human is currently expected to remember.

    The anchor check (IL001) guards the reserved-object rule: the protected ID-0
    `MainPage` display keeps its name. A rename compiles (display refs are by
    internal ID, so the build status carries no signal about it), and afterwards
    the SolutionCenter preview anchor is detached with nothing in the build to
    flag it. See KnowledgeBase/Conventions/Startup-Layout-and-MainPage.md and
    Working-Rules.md ("Names are identity"). A deterministic check catches
    exactly this class.

DESIGN (the 3-part discipline this implements)
    1. Prose -> deterministic check. Every check below is derived from a named
       repo rule/doc, not invented.
    2. Ratchet, don't boil the ocean. Day-one violations are grandfathered into
       an allow-list sidecar (invariant-lint.allow, one finding-key per line,
       '#' comments). The run FAILs only on NEW drift past that line.
       Re-seed deliberately with --reseed.
    3. Deterministic vs judgment are split. This script is the cheap mechanical
       pass. The "is this still the right invariant / refresh the conventions"
       pass is a separate human/AI cadence and is NOT a precondition for this.

PROPERTIES
    - READ-ONLY. Detects and reports; never mutates a solution, doc, or row.
      (Only --reseed writes, and only to the allow-list sidecar, on request.)
    - Takes the repo ROOT as an argument -> location- and version-independent.
    - Reads the plaintext DesignerData/<sol>-Designer/Git/*.json exports, NOT
      the encrypted .dbsln. No MCP, no runtime, no decrypt needed.
    - Exit 0 = clean (no unsanctioned FAIL). Exit 1 = at least one new FAIL.
      WARN never fails the run.
    - Confidentiality-safe: reports by site / object name / file path only.
      It never emits row payloads or restricted content.

USAGE
    python invariant_lint.py <ROOT>            # lint; exit 0/1
    python invariant_lint.py <ROOT> --list     # print check definitions, exit 0
    python invariant_lint.py <ROOT> --reseed   # add today's FAILs to allow-list
    python invariant_lint.py <ROOT> --quiet    # only WARN/FAIL lines + summary

ROOT is the FrameworX-Projects workspace root (the folder holding Sites/).
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ALLOW_PATH = os.path.join(HERE, "invariant-lint.allow")

# ---- check registry: definition + mechanical method + cost (for --list / docs)
CHECKS = {
    "IL001": {
        "title": "reserved-object integrity",
        "rule": "KnowledgeBase/Conventions/Startup-Layout-and-MainPage.md + "
                "Working-Rules.md ('Names are identity')",
        "definition": "Every in-tree solution export contains the protected "
                      "ID-0 home display named exactly 'MainPage' and the "
                      "predefined layout named exactly 'Startup'. No renamed "
                      "'MainPage_*' variant exists (the rename signature this "
                      "check looks for).",
        "method": "For each Sites/*/Solutions/DesignerData/*/Git/: read "
                  "Data[].Name from all DisplaysList-*.json (assert 'MainPage' "
                  "present; warn on any 'MainPage_*') and from all "
                  "DisplaysLayouts-*.json (assert 'Startup' present).",
        "cost": "low (a few small JSON reads per solution; ~ms).",
    },
    "IL001b": {
        "title": "Startup Content is a real page",
        "rule": "KnowledgeBase/Conventions/Startup-Layout-and-MainPage.md",
        "definition": "The Startup layout's Content region points at a display "
                      "that exists and is populated. 'Never finish a solution "
                      "with the Startup layout's Content region pointing at an "
                      "empty or placeholder page' (blank first screen + blank "
                      "SolutionCenter preview).",
        "method": "For each Git/: read DisplaysLayouts-Startup -> Members -> "
                  "the Content region's Page (strip a 'Display.' prefix). FAIL "
                  "if no Content page is set or it names a display absent from "
                  "DisplaysList-*.json. WARN if that display is unpopulated -- "
                  "content = Canvas 'Elements' OR Dashboard 'Cells' OR a 'Xaml' "
                  "body with a child control beyond the root <TDisplay> (a "
                  "Dashboard page keeps content in Cells, NOT Elements). Missing "
                  "Startup layout is left to IL001.",
        "cost": "low (one layout read + the display index already built; ~ms).",
    },
    "IL002": {
        "title": "project-layout conformance",
        "rule": "CLAUDE.md project table + INDEX.md + README.md Layout + "
                "Templates/SiteProject/",
        "definition": "Every Sites/<Name>/ carries the core folders "
                      "{Specifications, Solutions, Documentation, Decisions, "
                      "ChangeLogs}. Tests/ is recommended (WARN if absent).",
        "method": "For each Sites/<Name>/: stat each required subfolder. "
                  "Missing core folder -> FAIL; missing Tests -> WARN. Extra "
                  "folders are allowed (workspace scales).",
        "cost": "trivial (directory stat per site).",
    },
    "IL003": {
        "title": "solution presence + name hygiene",
        "rule": "KnowledgeBase/Conventions/Solution-File-Placement.md",
        "definition": "Every Sites/<Name>/Solutions/ that exists holds a "
                      ".dbsln OR a README.md recording where the solution "
                      "lives; every .dbsln stem is a clean bare name "
                      "(letters/digits/underscore, no spaces or hyphens), "
                      "because the name becomes the filename.",
        "method": "Glob Sites/*/Solutions/. If present and neither *.dbsln nor "
                  "README.md -> FAIL. For each *.dbsln, assert stem matches "
                  "^[A-Za-z0-9_]+$ -> FAIL otherwise.",
        "cost": "trivial (glob + regex).",
    },
}

FAIL, WARN, PASS = "FAIL", "WARN", "PASS"
CORE_FOLDERS = ["Specifications", "Solutions", "Documentation", "Decisions", "ChangeLogs"]
DBSLN_NAME_RE = re.compile(r"^[A-Za-z0-9_]+$")
MAINPAGE_VARIANT_RE = re.compile(r"^MainPage_.+")


class Finding:
    __slots__ = ("check", "severity", "key", "evidence")

    def __init__(self, check, severity, key, evidence):
        self.check = check
        self.severity = severity
        self.key = key          # stable, allow-list-matchable
        self.evidence = evidence


def _load_names(path):
    """Return list of Data[].Name from a FrameworX export file, or None on error."""
    try:
        with open(path, encoding="utf-8-sig") as f:
            doc = json.load(f)
    except Exception as e:                       # parse/IO problem is itself signal
        return ("ERROR", "%s" % e)
    data = doc.get("Data") if isinstance(doc, dict) else None
    if not isinstance(data, list):
        return []
    return [r.get("Name") for r in data if isinstance(r, dict) and r.get("Name")]


def _load_rows(path):
    """Return the Data list from an export file, or ('ERROR', msg) on failure."""
    try:
        with open(path, encoding="utf-8-sig") as f:
            doc = json.load(f)
    except Exception as e:
        return ("ERROR", "%s" % e)
    data = doc.get("Data") if isinstance(doc, dict) else None
    return data if isinstance(data, list) else []


def _startup_content_page(git):
    """Resolve the Startup layout's Content-region page name.

    Returns (display_name, "") on success, or (None, reason). 'Display.' is
    stripped from the page reference. A missing Startup layout returns
    (None, "no Startup layout") so IL001b can defer that case to IL001.
    """
    saw_startup = False
    for fn in sorted(os.listdir(git)):
        if not (fn.startswith("DisplaysLayouts-") and fn.endswith(".json")):
            continue
        rows = _load_rows(os.path.join(git, fn))
        if isinstance(rows, tuple):
            continue
        for layout in rows:
            if layout.get("Name") != "Startup":
                continue
            saw_startup = True
            members = layout.get("Members") or layout.get("Regions") or []
            for m in members:
                if str(m.get("Region", "")).lower() == "content":
                    pg = m.get("Page") or ""
                    if not pg:
                        return (None, "Content region present but Page empty")
                    name = pg.split(".", 1)[1] if pg.startswith("Display.") else pg
                    return (name, "")
            return (None, "no Content region in Startup layout")
    return (None, "no Startup layout" if not saw_startup else "unresolved")


def _sites(root):
    base = os.path.join(root, "Sites")
    if not os.path.isdir(base):
        return []
    return sorted(
        (name, os.path.join(base, name))
        for name in os.listdir(base)
        if os.path.isdir(os.path.join(base, name))
    )


def _git_dirs(site_path):
    """Yield each DesignerData/<sol>-Designer/Git directory under a site."""
    dd = os.path.join(site_path, "Solutions", "DesignerData")
    if not os.path.isdir(dd):
        return
    for sol in sorted(os.listdir(dd)):
        git = os.path.join(dd, sol, "Git")
        if os.path.isdir(git):
            yield sol, git


# ---------------------------------------------------------------- checks
def check_IL001(root):
    out = []
    for site, sp in _sites(root):
        for sol, git in _git_dirs(sp):
            disp_names, layout_names, parse_errs = [], [], []
            for fn in sorted(os.listdir(git)):
                full = os.path.join(git, fn)
                if fn.startswith("DisplaysList-") and fn.endswith(".json"):
                    r = _load_names(full)
                    if isinstance(r, tuple):
                        parse_errs.append(fn)
                    else:
                        disp_names += r
                elif fn.startswith("DisplaysLayouts-") and fn.endswith(".json"):
                    r = _load_names(full)
                    if isinstance(r, tuple):
                        parse_errs.append(fn)
                    else:
                        layout_names += r
            tag = "%s/%s" % (site, sol)
            if "MainPage" not in disp_names:
                out.append(Finding("IL001", FAIL, "IL001:%s:MainPage-missing" % tag,
                                   "no display named 'MainPage' in %s" % tag))
            for n in disp_names:
                if MAINPAGE_VARIANT_RE.match(n):
                    out.append(Finding("IL001", WARN, "IL001:%s:MainPage-variant:%s" % (tag, n),
                                       "rename-smell: display '%s' looks like a renamed MainPage in %s" % (n, tag)))
            if "Startup" not in layout_names:
                out.append(Finding("IL001", FAIL, "IL001:%s:Startup-missing" % tag,
                                   "no layout named 'Startup' in %s" % tag))
            for fn in parse_errs:
                out.append(Finding("IL001", WARN, "IL001:%s:parse:%s" % (tag, fn),
                                   "could not parse export %s (treated as WARN)" % fn))
    return out


def _is_populated(row):
    """A display has real content if it carries Canvas Elements, Dashboard Cells,
    or a Xaml body with a child control beyond the root <TDisplay>. A Dashboard
    page keeps its content in Cells (and Xaml), NOT in Elements -- counting only
    Elements falsely flags every Dashboard page as blank.
    """
    if row.get("Elements") or []:
        return True
    if row.get("Cells") or []:
        return True
    xaml = row.get("Xaml") or ""
    return xaml.count("<T") > 1          # >1 => a child T-control besides root <TDisplay>


def check_IL001b(root):
    out = []
    for site, sp in _sites(root):
        for sol, git in _git_dirs(sp):
            tag = "%s/%s" % (site, sol)
            content = {}                   # display name -> populated? (bool)
            for fn in sorted(os.listdir(git)):
                if fn.startswith("DisplaysList-") and fn.endswith(".json"):
                    rows = _load_rows(os.path.join(git, fn))
                    if isinstance(rows, tuple):
                        continue           # parse error already WARNed by IL001
                    for row in rows:
                        nm = row.get("Name")
                        if nm:
                            content[nm] = _is_populated(row)
            page, why = _startup_content_page(git)
            if page is None:
                if why == "no Startup layout":
                    continue               # IL001 owns the missing-Startup FAIL
                out.append(Finding("IL001b", FAIL, "IL001b:%s:Content-unset" % tag,
                                   "Startup Content region resolves to no page in %s (%s) "
                                   "-> blank first screen + preview" % (tag, why)))
                continue
            if page not in content:
                out.append(Finding("IL001b", FAIL, "IL001b:%s:Content-page-missing:%s" % (tag, page),
                                   "Startup Content points at display '%s' which does not "
                                   "exist in %s" % (page, tag)))
            elif not content[page]:
                out.append(Finding("IL001b", WARN, "IL001b:%s:Content-page-blank:%s" % (tag, page),
                                   "Startup Content page '%s' has no content (no Elements/"
                                   "Cells/Xaml children) in %s -> blank preview / first "
                                   "screen" % (page, tag)))
    return out


def check_IL002(root):
    out = []
    for site, sp in _sites(root):
        for folder in CORE_FOLDERS:
            if not os.path.isdir(os.path.join(sp, folder)):
                out.append(Finding("IL002", FAIL, "IL002:%s:missing-%s" % (site, folder),
                                   "%s/ missing core folder '%s'" % (site, folder)))
        if not os.path.isdir(os.path.join(sp, "Tests")):
            out.append(Finding("IL002", WARN, "IL002:%s:missing-Tests" % site,
                               "%s/ missing recommended folder 'Tests'" % site))
    return out


def check_IL003(root):
    out = []
    for site, sp in _sites(root):
        sol_dir = os.path.join(sp, "Solutions")
        if not os.path.isdir(sol_dir):
            continue  # absence of Solutions/ is IL002's concern, not IL003's
        # Ignore dotfiles and AppleDouble sidecars (._Foo.dbsln): they are gitignored,
        # never publish, and would otherwise FAIL the name check on a macOS clone.
        entries = [e for e in os.listdir(sol_dir) if not e.startswith(".")]
        dbslns = [e for e in entries if e.lower().endswith(".dbsln")]
        has_readme = any(e.lower() == "readme.md" for e in entries)
        if not dbslns and not has_readme:
            out.append(Finding("IL003", FAIL, "IL003:%s:no-dbsln-no-readme" % site,
                               "%s/Solutions/ has neither a .dbsln nor a README.md" % site))
        for db in sorted(dbslns):
            stem = db[:-len(".dbsln")]
            if not DBSLN_NAME_RE.match(stem):
                out.append(Finding("IL003", FAIL, "IL003:%s:dbsln-name:%s" % (site, db),
                                   "solution filename '%s' is not a clean bare name "
                                   "(letters/digits/underscore only)" % db))
    return out


CHECK_FNS = [check_IL001, check_IL001b, check_IL002, check_IL003]


# ---------------------------------------------------------------- allow-list
def load_allow():
    keys = set()
    if not os.path.exists(ALLOW_PATH):
        return keys
    with open(ALLOW_PATH, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            keys.add(s)
    return keys


def reseed(findings):
    """Append today's FAIL keys (not already present) to the allow-list."""
    existing = load_allow()
    new = [f for f in findings if f.severity == FAIL and f.key not in existing]
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    header = ("# invariant-lint allow-list (ratchet sidecar)\n"
              "# One sanctioned finding-key per line. '#' starts a comment.\n"
              "# A FAIL whose key is listed here is reported as ALLOWED and does\n"
              "# NOT fail the run. Remove a line to re-arm that check.\n")
    write_header = not os.path.exists(ALLOW_PATH)
    with open(ALLOW_PATH, "a", encoding="utf-8") as f:
        if write_header:
            f.write(header)
        if new:
            f.write("\n# --- re-seeded %s (review each: confirm it is truly sanctioned) ---\n" % stamp)
            for fnd in new:
                f.write("# %s\n%s\n" % (fnd.evidence, fnd.key))
    return len(new)


# ---------------------------------------------------------------- reporting
def print_list():
    print("Invariant linter, check definitions\n" + "=" * 64)
    for cid, c in CHECKS.items():
        print("\n%s  %s" % (cid, c["title"]))
        print("  rule:       %s" % c["rule"])
        print("  definition: %s" % c["definition"])
        print("  method:     %s" % c["method"])
        print("  cost:       %s" % c["cost"])


def run(root, quiet=False):
    allow = load_allow()
    findings = []
    for fn in CHECK_FNS:
        findings += fn(root)

    print("FrameworX-Projects invariant linter")
    print("root: %s" % os.path.abspath(root))
    print("allow-list: %s (%d sanctioned)" % (ALLOW_PATH, len(allow)))
    print("=" * 64)

    new_fail = 0
    by_check = {}
    for f in findings:
        by_check.setdefault(f.check, []).append(f)

    for cid in CHECKS:
        c = CHECKS[cid]
        items = by_check.get(cid, [])
        hard = [f for f in items if f.severity == FAIL]
        if not items:
            if not quiet:
                print("PASS   %s  %s" % (cid, c["title"]))
            continue
        for f in items:
            sanctioned = f.severity == FAIL and f.key in allow
            if f.severity == FAIL and not sanctioned:
                new_fail += 1
            mark = ("ALLOWED" if sanctioned else f.severity)
            if quiet and f.severity == PASS:
                continue
            print("%-7s %s  %s" % (mark, cid, f.evidence))
            if not sanctioned and f.severity == FAIL:
                print("           key: %s" % f.key)
        if not hard and not quiet:
            print("       (%s: no FAIL; %d WARN/info)" % (cid, len(items)))

    print("=" * 64)
    warns = sum(1 for f in findings if f.severity == WARN)
    sanctioned = sum(1 for f in findings if f.severity == FAIL and f.key in allow)
    print("FAIL(new)=%d  FAIL(sanctioned)=%d  WARN=%d  -> exit %d"
          % (new_fail, sanctioned, warns, 0 if new_fail == 0 else 1))
    return 0 if new_fail == 0 else 1


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = set(a for a in sys.argv[1:] if a.startswith("--"))
    if "--list" in flags:
        print_list()
        return 0
    if len(args) != 1:
        print(__doc__)
        return 2
    root = args[0]
    if not os.path.isdir(root):
        print("ROOT not a directory: %s" % root)
        return 2
    if "--reseed" in flags:
        findings = []
        for fn in CHECK_FNS:
            findings += fn(root)
        added = reseed(findings)
        print("Re-seed: added %d FAIL key(s) to %s" % (added, ALLOW_PATH))
        print("Review each new line and confirm it is truly sanctioned.")
        return 0
    return run(root, quiet="--quiet" in flags)


if __name__ == "__main__":
    sys.exit(main())
