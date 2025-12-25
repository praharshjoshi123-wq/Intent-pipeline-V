import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def compute_cohesion(embeddings: np.ndarray, centroid: np.ndarray) -> float:
    """
    Mean cosine similarity between cluster points and centroid
    """
    sims = cosine_similarity(embeddings, centroid.reshape(1, -1))
    return float(sims.mean())


def compute_inter_cluster_similarity(centroids: list) -> float:
    """
    Mean cosine similarity between cluster centroids
    """
    if len(centroids) < 2:
        return 1.0

    sims = cosine_similarity(centroids)
    upper = sims[np.triu_indices(len(centroids), k=1)]
    return float(upper.mean())
