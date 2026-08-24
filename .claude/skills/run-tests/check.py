#!/usr/bin/env python
"""
Checker for the FrameworX Solution Workspace test harness.

Compares collected product data (actual.json, gathered over the Designer/Console
and Runtime MCP per .claude/skills/run-tests/collect-live.md) against the golden
expectations (expected.json). Runs two assertion sets:

  - structure: counts and domain UserTypes. Deterministic. The collected numbers
    are stable across re-takes of the same built solution.
  - live: runtime invariants (present, good quality, recent, in range, moved).
    Tolerant, because a simulated process value changes between reads.

Why collected data and not a direct file read: a FrameworX .dbsln is an
ENCRYPTED SQLite file. The product decrypts it through its own SQLite library;
a plain sqlite3 reader sees "file is not a database". So every structure read
goes through the MCP (the product decrypts), or through an exported JSON
workspace, never by cracking the binary. See KnowledgeBase/References/dbsln-format-note.md.

Usage:
    python .claude/skills/run-tests/check.py <expected.json> <actual.json> [--structure-only]

  --structure-only runs just the deterministic structural gate (useful in CI,
  or as the golden-vs-retake determinism check).

Exit code 0 = all assertions passed. Non-zero = at least one failed.

Expected `live.tags[]` invariants (tolerant by design, because a simulated
process value moves between reads):
    qualityGood   -> collected `quality` contains "good" (case-insensitive)
    maxAgeSeconds -> collected `read2.ageSeconds` <= maxAgeSeconds
    range         -> read2.value within [min, max]
    mustMove      -> read1.value != read2.value
"""
import json
import sys


def dig(d, dotted):
    cur = d
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


PRESENCE_KEYS = {"domain", "domainTagsPresent", "domainUserTypes", "present"}


def _leaves(prefix, node):
    """Yield (dotted_path, key, value) for every leaf in the expected structure."""
    for k, v in node.items():
        path = "%s.%s" % (prefix, k) if prefix else k
        if isinstance(v, dict):
            for item in _leaves(path, v):
                yield item
        else:
            yield path, k, v


def check_structure(expected, actual, results):
    """Schema-driven: the shape of expected.structure decides each assertion.

      list under a presence key  -> every named item must appear in the actual list
      int, key ends in 'Min'     -> actual >= expected
      int, key ends in 'Max'     -> actual <= expected
      int otherwise              -> actual == expected (exact count)
    """
    es, as_ = expected.get("structure", {}), actual.get("structure", {})
    for path, key, want in _leaves("", es):
        got = dig(as_, path)
        label = "structure.%s" % path
        if isinstance(want, list) and key in PRESENCE_KEYS:
            found = set(got or [])
            missing = [n for n in want if n not in found]
            results.append((not missing, label,
                            "all present" if not missing else "missing: %s" % ", ".join(missing)))
        elif isinstance(want, (int, float)) and not isinstance(want, bool):
            # For Min/Max thresholds, the actual file carries the natural key
            # (e.g. expected 'security.userCountMin' reads actual 'security.userCount').
            if key.endswith(("Min", "Max")):
                got = dig(as_, path[:-3])
            gi = got if isinstance(got, (int, float)) and not isinstance(got, bool) else None
            if key.endswith("Min"):
                results.append((gi is not None and gi >= want, label, "got %s (min %s)" % (got, want)))
            elif key.endswith("Max"):
                results.append((gi is not None and gi <= want, label, "got %s (max %s)" % (got, want)))
            else:
                results.append((got == want, label, "expected %s, got %s" % (want, got)))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def check_live(expected, actual, results):
    want_tags = dig(expected, "live.tags") or []
    got_tags = {t.get("id"): t for t in (dig(actual, "live.tags") or [])}
    for spec in want_tags:
        tid = spec.get("id", "?")
        got = got_tags.get(tid)
        if got is None:
            results.append((False, "live.%s" % tid, "no collected reading"))
            continue
        path = got.get("resolvedPath") or ""
        r1, r2 = got.get("read1") or {}, got.get("read2") or {}
        v1, v2 = num(r1.get("value")), num(r2.get("value"))

        results.append((bool(path) and v2 is not None,
                        "live.%s.present" % tid,
                        "resolved=%r value2=%r" % (path, r2.get("value"))))

        if spec.get("qualityGood"):
            q = str(got.get("quality", "")).lower()
            results.append(("good" in q, "live.%s.quality" % tid, "quality=%r" % got.get("quality")))

        max_age = spec.get("maxAgeSeconds")
        if max_age is not None:
            age = num(r2.get("ageSeconds"))
            results.append((age is not None and age <= max_age,
                            "live.%s.fresh" % tid,
                            "ageSeconds=%r (max %s)" % (r2.get("ageSeconds"), max_age)))

        rng = spec.get("range")
        if rng and v2 is not None:
            results.append((rng[0] <= v2 <= rng[1], "live.%s.range" % tid,
                            "value=%s in [%s, %s]" % (v2, rng[0], rng[1])))

        if spec.get("mustMove"):
            moved = v1 is not None and v2 is not None and v1 != v2
            results.append((moved, "live.%s.moved" % tid,
                            "read1=%r read2=%r" % (r1.get("value"), r2.get("value"))))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    if len(args) != 2:
        print(__doc__)
        return 2
    structure_only = "--structure-only" in flags
    with open(args[0], encoding="utf-8") as f:
        expected = json.load(f)
    with open(args[1], encoding="utf-8") as f:
        actual = json.load(f)

    results = []
    check_structure(expected, actual, results)
    if not structure_only:
        check_live(expected, actual, results)

    mode = "structural gate" if structure_only else "full gate (structure + live)"
    print("Checker [%s]: %s" % (mode, expected.get("solution", "?")))
    print("-" * 64)
    failed = 0
    for ok, label, detail in results:
        mark = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
        print("  %s  %-28s %s" % (mark, label, detail))
    print("-" * 64)
    total = len(results)
    print("%d/%d assertions passed." % (total - failed, total))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
