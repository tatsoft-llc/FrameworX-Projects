# AISessions: per-session scratch

Claude's working notes live here: mid-task state, cold-start resume files (the `cold-start-prepare` / `cold-start-resume` skills, in the
[companion repo](https://github.com/tatsoft-llc/Claude-Code-Skills)), session-scoped analysis. **Never the deliverable**: deliverables land in the
project folders (`Sites/<Name>/…`) or `KnowledgeBase/`.

Everything in this folder except this README is git-ignored, so scratch never ships with your repository.

## Unfinished work leaves with a handoff

A session that must stop before its work is done writes the handoff **before** it stops: a resume file
here (the `cold-start-prepare` skill), or a continuation prompt in its closing message, naming what is
finished, what is not, and the exact next action. A ChangeLog line is history, not a handoff; the next
session should never have to re-derive in-flight state from the log alone.
