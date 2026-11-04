"""MCP boundary between the application repository and the separate Obsidian vault."""

import os
import re
import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP


TYPE_DIRS = {'concept': 'Concepts', 'component': 'Components',
             'decision': 'Decisions', 'glossary': 'Glossary'}


class VaultService:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        if not self.root.is_dir() or not (self.root/'.git').exists():
            raise ValueError('Vault must be an existing separate git repository')

    def _git(self, *args):
        return subprocess.run(['git', *args], cwd=self.root, check=True,
                              capture_output=True, text=True).stdout.strip()

    def _note_path(self, title: str, note_type: str) -> Path:
        if note_type not in TYPE_DIRS:
            raise ValueError('Unsupported note type')
        if not re.fullmatch(r'[\w\- ]{2,80}', title, re.UNICODE):
            raise ValueError('Title contains unsupported characters')
        path = (self.root / TYPE_DIRS[note_type] / f'{title}.md').resolve()
        if not path.is_relative_to(self.root):
            raise ValueError('Invalid note path')
        return path

    def ingest_note(self, title: str, note_type: str, content: str,
                    links: list[str] | None = None) -> dict:
        """Create or update one note, commit and push only if its content changes."""
        path = self._note_path(title.strip(), note_type)
        if not content.strip():
            raise ValueError('Note content is required')
        if 'origin' in self._git('remote').splitlines():
            self._git('pull', '--ff-only', 'origin', 'main')
        linked = []
        for name in links or []:
            if not re.fullmatch(r'[\w\- ]{2,80}', name, re.UNICODE):
                raise ValueError('Invalid link')
            linked.append(f'- [[{name}]]')
        body = (f'---\ntype: {note_type}\ntags:\n  - development\n---\n\n'
                f'# {title.strip()}\n\n{content.strip()}\n')
        if linked:
            body += '\n## Зв’язки\n' + '\n'.join(linked) + '\n'
        old = path.read_text(encoding='utf8') if path.exists() else None
        if old == body:
            return {'status': 'unchanged', 'path': str(path.relative_to(self.root))}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding='utf8')
        self._git('add', '--', str(path.relative_to(self.root)))
        self._git('commit', '-m', f'Knowledge: {title.strip()}')
        if 'origin' in self._git('remote').splitlines():
            self._git('push', 'origin', 'main')
        return {'status': 'created' if old is None else 'updated',
                'path': str(path.relative_to(self.root))}

    def get_note(self, title: str) -> dict:
        for path in self._all_notes():
            if path.stem.casefold() == title.strip().casefold():
                return {'title': path.stem, 'path': str(path.relative_to(self.root)),
                        'content': path.read_text(encoding='utf8')}
        return {'error': 'Note not found', 'title': title}

    def _all_notes(self) -> list[Path]:
        return sorted(p for folder in TYPE_DIRS.values()
                      for p in (self.root/folder).glob('*.md'))

    def search_notes(self, query: str, limit: int = 5) -> list[dict]:
        """Find notes with semantic vectors; lexical mode is retained for evaluation."""
        if os.getenv('STUDYFLOW_RETRIEVAL_MODE', 'semantic') == 'semantic':
            from .vector_index import search
            notes = [(str(p.relative_to(self.root)), p.read_text(encoding='utf8'))
                     for p in self._all_notes()]
            return search(notes, query, limit)
        return self.search_notes_lexical(query, limit)

    def search_notes_lexical(self, query: str, limit: int = 5) -> list[dict]:
        """Original PR3 exact-word baseline, kept for the same-question comparison."""
        if not query.strip():
            return []
        words = query.casefold().split()
        scored = []
        for path in self._all_notes():
            body = path.read_text(encoding='utf8')
            text = (path.stem + ' ' + body).casefold()
            score = sum(text.count(word) for word in words)
            if score:
                scored.append((score, path, body))
        scored.sort(key=lambda item: (-item[0], item[1].name))
        return [{'title': p.stem, 'path': str(p.relative_to(self.root)),
                 'score': float(score), 'content': body[:1200]}
                for score, p, body in scored[:max(1, min(limit, 10))]]


mcp = FastMCP('studyflow-vault')


def service():
    return VaultService(os.environ['STUDYFLOW_VAULT_PATH'])


@mcp.tool()
def ingest_note(title: str, note_type: str, content: str,
                links: list[str] | None = None) -> dict:
    """Create or update a typed Obsidian note, commit and push it."""
    return service().ingest_note(title, note_type, content, links)


@mcp.tool()
def get_note(title: str) -> dict:
    """Return one Obsidian note by exact title."""
    return service().get_note(title)


@mcp.tool()
def search_notes(query: str, limit: int = 5) -> list[dict]:
    """Find relevant Obsidian notes using the current retrieval index."""
    return service().search_notes(query, limit)


def main():
    service()  # fail early if configuration is invalid
    mcp.run(transport='stdio')


if __name__ == '__main__':
    main()
