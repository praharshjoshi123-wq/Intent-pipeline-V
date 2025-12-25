"""
run_pipeline.py

End-to-end orchestrator for intent expansion pipeline.
This file wires together:
- baseline intent assignment (assumed pre-existing)
- clustering
- decision rules
- proposal output

This file contains NO intelligence.
"""

import json
from collections import defaultdict

from clustering.clustering import cluster_bucket
from decisions.decisions import decide_action


# -------------------------
# STEP 1: Load data
# -------------------------

def load_messages(path: str):
    """
    Expected input JSON format:
    [
      {
        "message_id": "...",
        "text": "...",
        "primary_intent": "...",
        "secondary_intent": "...",
        "embedding": [...]
      }
    ]
    """
    with open(path, "r") as f:
        return json.load(f)


# -------------------------
# STEP 2: Group into buckets
# -------------------------

def bucket_messages(messages):
    """
    Groups messages by (primary_intent, secondary_intent)
    """
    buckets = defaultdict(list)

    for msg in messages:
        key = (msg["primary_intent"], msg["secondary_intent"])
        buckets[key].append({
            "message_id": msg["message_id"],
            "embedding": msg["embedding"]
        })

    return buckets


# -------------------------
# STEP 3: Run pipeline
# -------------------------

def run_pipeline(input_path: str, output_path: str):
    messages = load_messages(input_path)
    buckets = bucket_messages(messages)

    results = []

    for (primary, secondary), bucket_msgs in buckets.items():
        bucket = {
            "primary_intent": primary,
            "secondary_intent": secondary,
            "messages": bucket_msgs
        }

        # ---- Clustering ----
        bucket_metrics = cluster_bucket(bucket)

        # ---- Decision ----
        decision = decide_action(bucket_metrics)

        # ---- Collect output ----
        results.append({
            "primary_intent": primary,
            "secondary_intent": secondary,
            "decision": decision,
            "metrics": {
                "message_count": bucket_metrics.get("message_count"),
                "clusters": bucket_metrics.get("clusters"),
                "inter_cluster_similarity": bucket_metrics.get("inter_cluster_similarity"),
                "noise_ratio": bucket_metrics.get("noise_ratio")
            }
        })

    # -------------------------
    # STEP 4: Save results
    # -------------------------

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Pipeline complete. Results saved to {output_path}")


# -------------------------
# ENTRY POINT
# -------------------------

if __name__ == "__main__":
    INPUT_PATH = "data/messages_with_embeddings.json"
    OUTPUT_PATH = "outputs/decision_results.json"

    run_pipeline(INPUT_PATH, OUTPUT_PATH)
