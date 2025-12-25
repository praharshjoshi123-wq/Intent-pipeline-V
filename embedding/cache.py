import hashlib
import json
import os

CACHE_PATH = "outputs/embedding_cache.json"


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_cache():
    if not os.path.exists(CACHE_PATH):
        return {}
    with open(CACHE_PATH, "r") as f:
        return json.load(f)


def save_cache(cache: dict):
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f)


def get_cached_embedding(text: str, cache: dict):
    return cache.get(_hash_text(text))


def set_cached_embedding(text: str, embedding, cache: dict):
    cache[_hash_text(text)] = embedding
