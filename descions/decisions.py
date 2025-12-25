from thresholds import *


def decide_action(bucket_metrics: dict) -> dict:
    clusters = bucket_metrics["clusters"]
    total_msgs = bucket_metrics["message_count"]
    inter_sim = bucket_metrics.get("inter_cluster_similarity", 1.0)


    # NO DATA GUARD
  
    if total_msgs < MIN_BUCKET_SIZE_SPLIT:
        return _no_action("too_few_messages")


    # FLAG → MISSING INTENT

    if bucket_metrics["secondary_intent"] == "FLAG":
        for c in clusters:
            if (
                c["size"] >= MIN_BUCKET_SIZE_MISSING
                and c["cohesion"] >= MIN_COHESION_MISSING
            ):
                return _missing_intent(c)
        return _no_action("flag_but_no_clear_pattern")

    # KEEP
   
    dominant = max(clusters, key=lambda c: c["size"])
    if (
        dominant["size"] / total_msgs >= DOMINANT_CLUSTER_RATIO
        and dominant["cohesion"] >= MIN_COHESION_KEEP
    ):
        return _keep()

    # SPLIT
    
    for c in clusters:
        if (
            c["size"] / total_msgs >= MIN_CLUSTER_RATIO
            and c["cohesion"] >= MIN_COHESION_SPLIT
            and inter_sim <= MAX_INTER_CLUSTER_SIMILARITY_SPLIT
        ):
            return _split(c)

  
    # MERGE
    
    if inter_sim >= MIN_INTER_CLUSTER_SIMILARITY_MERGE:
        return _merge()

    
    # DEFAULT
   
    return _no_action("ambiguous_or_noisy")
def _split(cluster):
    return {
        "action": "SPLIT",
        "confidence": "high",
        "justification": {
            "reason": "cohesive_subcluster_detected",
            "cluster_size": cluster["size"],
            "cohesion": cluster["cohesion"],
        },
    }


def _missing_intent(cluster):
    return {
        "action": "MISSING_INTENT",
        "confidence": "high",
        "justification": {
            "reason": "cohesive_pattern_in_flag",
            "cluster_size": cluster["size"],
            "cohesion": cluster["cohesion"],
        },
    }


def _merge():
    return {
        "action": "MERGE",
        "confidence": "medium",
        "justification": {
            "reason": "high_inter_cluster_similarity"
        },
    }


def _keep():
    return {
        "action": "KEEP",
        "confidence": "high",
        "justification": {
            "reason": "single_dominant_cluster"
        },
    }


def _no_action(reason: str):
    return {
        "action": "NO_ACTION_FLAG",
        "confidence": "low",
        "justification": {
            "reason": reason
        },
    }
