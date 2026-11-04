---
name: record-decision
description: Record a real StudyFlow architecture decision as an Obsidian ADR via the vault MCP connector.
---

# Record a StudyFlow decision

1. Read `docs/app-requirements.md`, `docs/guardrails.md` and the relevant code or configuration.
2. Call `studyflow-vault.search_notes` to find related existing decisions. If one exists, update it with the same title; otherwise choose a stable new title.
3. Write a short ADR with context, decision, rationale, alternatives and consequences. Distinguish current implementation from future plans.
4. Call `studyflow-vault.ingest_note` with `note_type: decision` and appropriate wiki-link targets. Do not write vault files directly.
5. Call `get_note` to verify the result and report status, path and evidence from the code. Repeated identical calls should return `unchanged`.

Respect `docs/guardrails.md`: the skill may update vault through MCP but must not push the application repository or remove decisions.
