# ChangeLog Convention: per-author files

How every project records *what changed and when*. Per-author files avoid merge conflicts when multiple
people or sessions work concurrently on the same project.

---

## The shape

Each site keeps a **`ChangeLogs/` folder**, not a single file, and inside it, **one file per contributor**:

```text
Sites/<Name>/
├── ChangeLogs/
│   ├── ChangeLog-jsmith.md     one file per person, you only ever append to your own
│   └── ChangeLog-<user>.md
└── Decisions/                  the "how & why" companion (one file per topic)
```

**Why per-author.** Two people appending to one shared `ChangeLog.md` collide on the same top-of-file region
every time they sync. One file per author means each person only ever edits their own. Concurrent work never
conflicts. A site worked by one person is fine with a single `ChangeLog-<user>.md`. The folder costs
nothing and means a second contributor never forces a restructure later.

## Naming

- `ChangeLog-<your-login>.md`: lowercase login / first name. The site folder already namespaces it, so no
  project or version in the filename.
- **One file per *person*, not per login.** If you sign in under `jsmith`, `john`, or `john.smith`, they are
  all the same person → all go in ONE file (e.g. `ChangeLog-jsmith.md`). Do NOT create per-login sibling files.

## Inside a file

Newest first (reverse-chronological). Group by date; one line per meaningful change. Keep entries short. The
deep "how & why" goes one-file-per-topic in `Decisions/`, and the ChangeLog entry links to it. Header template:

```markdown
# ChangeLog: <ProjectName> (<Author>)

Per-author changelog (house convention: see KnowledgeBase/Conventions/ChangeLog-Convention.md). Newest
first. Companion to `Decisions/` (what vs why).

> **Authorship note:** entries under `jsmith` / `john` / `john.smith` are all the same person,
> one canonical file, no per-login siblings.

---

## <YYYY-MM-DD>
- <what changed>. See `Decisions/<topic>.md` for why.
```

## Append-only discipline

New entries are **appended**, never whole-file rewrites. An in-place correction to an existing entry uses an
anchored, single-match edit. Never regenerate the file wholesale: parallel sessions working the same project
silently destroy each other's entries otherwise.

## Reading the log

"Check the ChangeLog" now means **scan the `ChangeLogs/` folder** (all authors), not open one file. Recent
entries across the per-author files are the highest-signal source for what just changed.

## Relationship to Decisions/

Unchanged: `ChangeLogs/` says **what changed and when**; `Decisions/` says **how & why** (one note per topic.
the same one-file-per-thing shape that keeps it conflict-free). A decision that helps *other* projects is
promoted to `KnowledgeBase/`.
