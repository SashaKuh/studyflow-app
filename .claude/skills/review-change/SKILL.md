---
name: review-change
description: Review a StudyFlow code change against project requirements, guardrails and vault knowledge, with concise findings and evidence.
---

# Review a StudyFlow change

Use for a real module, feature or diff in this repository.

1. Read the relevant requirement in `docs/app-requirements.md` and rule in `docs/guardrails.md`.
2. Call `studyflow-vault.search_notes` for architecture or decision context; call `get_note` for a precise note if needed. Do not read the vault directly.
3. Inspect the requested source and tests. Check behavior, error handling, SQL safety, and consistency with the architecture.
4. Run a targeted test when possible. Do not modify code as part of the review.
5. Return: scope; knowledge used; findings ordered by severity with file/line evidence; test command and result; remaining uncertainty. Say explicitly when no finding is confirmed.

Block rules from `docs/guardrails.md` still apply; do not push or delete files.
