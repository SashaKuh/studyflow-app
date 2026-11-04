"""Claude Code PreToolUse guardrail. Reads one JSON event from stdin."""

import json
import re
import sys


def check_action(event: dict) -> tuple[str | None, str | None]:
    name = event.get('tool_name', '')
    data = event.get('tool_input') or {}
    if name in ('Write', 'Edit'):
        path = str(data.get('file_path', '')).replace('\\', '/')
        if '/studyflow-knowledge-base/Decisions/' in path or '/Decisions/' in path:
            return 'deny', 'Рішення vault змінюються лише через MCP ingest_note'
        if path.endswith('/studyflow/storage.py') or path.endswith('/studyflow/domain.py'):
            return 'ask', 'Зміна ядра застосунку потребує перегляду'
    if name == 'Bash':
        cmd = str(data.get('command', ''))
        if re.search(r'\bgit\s+push\b[^\n;]*\bmain\b', cmd):
            return 'deny', 'Прямий push у main заборонено для агента'
        if re.search(r'\brm\s+-[^\s]*(?:r[^\s]*f|f[^\s]*r)', cmd):
            return 'deny', 'Руйнівне видалення заборонено'
        if re.search(r'\bALTER\s+TABLE\b', cmd, re.I):
            return 'ask', 'Міграція схеми потребує перегляду'
        if re.search(r'\bgit\s+commit\b', cmd):
            return 'ask', 'Коміт агента потребує перегляду'
    return None, None


def main():
    event = json.load(sys.stdin)
    decision, reason = check_action(event)
    if decision:
        print(json.dumps({'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'permissionDecision': decision,
            'permissionDecisionReason': reason
        }}, ensure_ascii=False))


if __name__ == '__main__':
    main()
