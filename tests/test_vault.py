from pathlib import Path
import subprocess

from harness.vault_server import VaultService


def test_ingest_idempotent_and_retrievable(tmp_path):
    subprocess.run(['git', 'init', '-b', 'main', str(tmp_path)], check=True, capture_output=True)
    subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=tmp_path, check=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=tmp_path, check=True)
    svc = VaultService(tmp_path)
    first = svc.ingest_note('Рішення щодо CSV', 'decision', 'CSV — лише експорт.', ['Локальне зберігання'])
    assert first['status'] == 'created'
    assert svc.ingest_note('Рішення щодо CSV', 'decision', 'CSV — лише експорт.', ['Локальне зберігання'])['status'] == 'unchanged'
    assert len(list((tmp_path/'Decisions').glob('*.md'))) == 1
    assert 'CSV — лише експорт.' in svc.get_note('Рішення щодо CSV')['content']
    assert svc.search_notes('CSV')[0]['title'] == 'Рішення щодо CSV'
    assert svc.ingest_note('Рішення щодо CSV', 'decision', 'CSV — резервний формат.')['status'] == 'updated'
