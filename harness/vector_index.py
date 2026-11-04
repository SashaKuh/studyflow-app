"""Embedded multilingual vector index derived from the Obsidian Markdown vault."""

import hashlib
import json
from functools import lru_cache
from pathlib import Path

import numpy as np
from fastembed import TextEmbedding


MODEL = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
APP_ROOT = Path(__file__).resolve().parents[1]
CACHE = APP_ROOT/'.cache'


@lru_cache(maxsize=1)
def model():
    return TextEmbedding(model_name=MODEL, cache_dir=str(CACHE/'models'))


def _normalize(vectors):
    arr = np.asarray(vectors, dtype=np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    return arr / np.maximum(norms, 1e-12)


def load_or_build(notes: list[tuple[str, str]]) -> tuple[list[dict], np.ndarray]:
    """Use one whole note as one chunk; rebuild when vault content changes."""
    CACHE.mkdir(parents=True, exist_ok=True)
    source = json.dumps(notes, ensure_ascii=False, sort_keys=True)
    fingerprint = hashlib.sha256(source.encode('utf8')).hexdigest()
    metadata_path = CACHE/'index.json'
    vectors_path = CACHE/'index.npy'
    if metadata_path.exists() and vectors_path.exists():
        metadata = json.loads(metadata_path.read_text(encoding='utf8'))
        if metadata.get('fingerprint') == fingerprint and metadata.get('model') == MODEL:
            return metadata['chunks'], np.load(vectors_path)
    chunks = [{'path': path, 'title': Path(path).stem, 'content': body[:1600]}
              for path, body in notes]
    texts = [c['title'] + '\n' + c['content'] for c in chunks]
    vectors = _normalize(list(model().embed(texts))) if texts else np.zeros((0, 384), dtype=np.float32)
    np.save(vectors_path, vectors)
    metadata_path.write_text(json.dumps({'fingerprint': fingerprint, 'model': MODEL,
                                         'chunking': 'one note per chunk', 'chunks': chunks},
                                        ensure_ascii=False, indent=2), encoding='utf8')
    return chunks, vectors


def search(notes: list[tuple[str, str]], query: str, limit: int = 5) -> list[dict]:
    if not query.strip():
        return []
    chunks, vectors = load_or_build(notes)
    if not chunks:
        return []
    q = _normalize(list(model().query_embed(query)))[0]
    scores = vectors @ q
    order = np.argsort(-scores)[:max(1, min(limit, 10))]
    return [{**chunks[int(i)], 'score': round(float(scores[i]), 4)} for i in order]
