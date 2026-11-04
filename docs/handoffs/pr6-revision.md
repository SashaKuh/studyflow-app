# Revision after Reviewer feedback

Reviewer returned `changes requested`. The first implementation passed 24 tests but left requirements and vault notes stale; `upcoming --days -1` also created an empty SQLite file before validating the argument.

I kept the separate `studyflow/upcoming.py` module and documented it in `docs/app-requirements.md`. This follows the W1 hook without changing `domain.py` or `storage.py`; the rationale and the SQL alternative are recorded in the vault decision `Фільтрація upcoming в окремому модулі`. The CLI now validates N before opening the store, and the test asserts that invalid N creates no database file. `CLI-команди` was updated through MCP. Changes are on `pr6-upcoming`, not on `main`.

Verification: `../../.venv/bin/python -m pytest -q` → 24 passed.
