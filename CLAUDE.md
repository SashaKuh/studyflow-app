# StudyFlow project instructions

- Read `ЗАВДАННЯ.md`, `docs/app-requirements.md`, `docs/guardrails.md` before proposing changes.
- The Obsidian vault is a separate repository. Use only `studyflow-vault` MCP tools to read or update it from Claude Code. Do not try to access the vault through Bash or file tools.
- Run the relevant tests after a code change and report the exact command and result.
- The course Python environment and pytest are in `../../.venv/bin/`; run tests with `../../.venv/bin/python -m pytest -q`.
- Do not push directly to `main` from the agent session. The project hook enforces this rule.
- Prefer small, traceable changes and concise handoffs with the reason for each decision.
