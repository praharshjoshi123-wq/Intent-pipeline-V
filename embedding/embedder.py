import json
from typing import List, Dict
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

from embedding.cache import (
    load_cache,
    save_cache,
    get_cached_embedding,
    set_cached_embedding,
)


# -----------------------
# Configuration
# -----------------------

MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 64
OUTPUT_PATH = "outputs/embeddings.json"


# -----------------------
# Preprocessing
# -----------------------

def preprocess(text: str) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    return text


# -----------------------
# Embedding Pipeline
# -----------------------

def embed_messages(messages: List[Dict]) -> List[Dict]:
    model = SentenceTransformer(MODEL_NAME)
    cache = load_cache()

    texts_to_embed = []
    index_map = []

    results = []

    # Step 1: preprocess + cache lookup
    for idx, msg in enumerate(messages):
        clean_text = preprocess(msg["text"])
        if not clean_text:
            continue

        cached = get_cached_embedding(clean_text, cache)
        if cached is not None:
            results.append({
                "message_id": msg["message_id"],
                "primary_intent": msg["primary_intent"],
                "secondary_intent": msg.get("secondary_intent"),
                "embedding": cached,
            })
        else:
            texts_to_embed.append(clean_text)
            index_map.append(idx)

    # Step 2: batch embedding
    for i in tqdm(range(0, len(texts_to_embed), BATCH_SIZE)):
        batch_texts = texts_to_embed[i:i + BATCH_SIZE]
        embeddings = model.encode(batch_texts, show_progress_bar=False)

        for text, emb in zip(batch_texts, embeddings):
            set_cached_embedding(text, emb.tolist(), cache)

    save_cache(cache)

    # Step 3: assemble final output
    for idx in index_map:
        msg = messages[idx]
        clean_text = preprocess(msg["text"])
        emb = get_cached_embedding(clean_text, cache)

        results.append({
            "message_id": msg["message_id"],
            "primary_intent": msg["primary_intent"],
            "secondary_intent": msg.get("secondary_intent"),
            "embedding": emb,
        })

    return results


# -----------------------
# Runner
# -----------------------

if __name__ == "__main__":
    with open("data/messages.json", "r") as f:
        messages = json.load(f)

    embedded = embed_messages(messages)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(embedded, f)

    print(f"Saved {len(embedded)} embeddings to {OUTPUT_PATH}")
