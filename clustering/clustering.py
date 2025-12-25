import numpy as np
import hdbscan
from sklearn.metrics.pairwise import cosine_similarity

from .metrics import compute_cohesion, compute_inter_cluster_similarity


def cluster_bucket(bucket: dict) -> dict:
    """
    Input:
        bucket = {
            primary_intent,
            secondary_intent,
            messages: [{message_id, embedding}]
        }

    Output:
        bucket_metrics (fed into decision layer)
    """

    messages = bucket["messages"]
    embeddings = np.array([m["embedding"] for m in messages])

    if len(embeddings) < 5:
        return _no_cluster_output(bucket, "too_few_messages")

    # -------------------
    # Run HDBSCAN
    # -------------------
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=max(5, int(0.1 * len(embeddings))),
        metric="euclidean"
    )

    labels = clusterer.fit_predict(embeddings)

    # -------------------
    # Group by cluster
    # -------------------
    clusters = {}
    for msg, label in zip(messages, labels):
        if label == -1:
            continue
        clusters.setdefault(label, []).append(msg["embedding"])

    cluster_outputs = []
    centroids = []

    for cluster_id, embs in clusters.items():
        embs = np.array(embs)
        centroid = embs.mean(axis=0)
        cohesion = compute_cohesion(embs, centroid)

        centroids.append(centroid)

        cluster_outputs.append({
            "cluster_id": int(cluster_id),
            "size": len(embs),
            "cohesion": round(cohesion, 3)
        })

    inter_sim = compute_inter_cluster_similarity(centroids)
    noise_ratio = float((labels == -1).sum() / len(labels))

    return {
        "primary_intent": bucket["primary_intent"],
        "secondary_intent": bucket["secondary_intent"],
        "message_count": len(messages),
        "clusters": cluster_outputs,
        "inter_cluster_similarity": inter_sim,
        "noise_ratio": round(noise_ratio, 3)
    }


def _no_cluster_output(bucket, reason):
    return {
        "primary_intent": bucket["primary_intent"],
        "secondary_intent": bucket["secondary_intent"],
        "message_count": len(bucket["messages"]),
        "clusters": [],
        "inter_cluster_similarity": 1.0,
        "noise_ratio": 1.0,
        "reason": reason
    }
