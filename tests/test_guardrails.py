import importlib.util
from pathlib import Path

import pytest


path = Path(__file__).parents[1]/'.claude/hooks/guardrail.py'
spec = importlib.util.spec_from_file_location('guardrail', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.mark.parametrize('event,expected', [
    ({'tool_name':'Read','tool_input':{'file_path':'docs/app-requirements.md'}}, None),
    ({'tool_name':'Bash','tool_input':{'command':'pytest -q'}}, None),
    ({'tool_name':'mcp__studyflow-vault__search_notes','tool_input':{'query':'SQLite'}}, None),
    ({'tool_name':'Edit','tool_input':{'file_path':'/repo/studyflow/storage.py'}}, 'ask'),
    ({'tool_name':'Bash','tool_input':{'command':'sqlite3 demo.db "ALTER TABLE tasks ADD x TEXT"'}}, 'ask'),
    ({'tool_name':'Bash','tool_input':{'command':'git commit -m update'}}, 'ask'),
    ({'tool_name':'Bash','tool_input':{'command':'git push origin main'}}, 'deny'),
    ({'tool_name':'Bash','tool_input':{'command':'rm -rf data'}}, 'deny'),
    ({'tool_name':'Write','tool_input':{'file_path':'/repo/studyflow-knowledge-base/Decisions/X.md'}}, 'deny'),
])
def test_guardrail_scenarios(event,expected):
    assert module.check_action(event)[0] == expected
