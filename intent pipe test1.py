import re
from typing import List
def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_customer_messages(history: str, max_turns: int = 2) -> List[str]:
    if not history:
        return []

    turns = history.split(" - ")
    customer_msgs = []

    for turn in turns:
        turn = turn.strip()
        if turn.startswith("human:"):
            customer_msgs.append(turn.replace("human:", "").strip())

    return customer_msgs[-max_turns:]


def build_text_for_analysis(history: str, current_message: str) -> str:
    parts = extract_customer_messages(history)
    parts.append(current_message)
    return clean_text(" ".join(parts))


# -----------------------
# Primary Intent Signals
# -----------------------

BASIC_INTERACTION_TOKENS = {
    "hi", "hello", "hey",
    "ok", "okay",
    "thanks", "thank", "thankyou",
    "got", "alright", "bye"
}

LOGISTICS_KEYWORDS = {
    "order", "delivery", "deliver", "delivered",
    "refund", "return", "cancel",
    "tracking", "track", "shipment",
    "rto", "courier",
    "payment", "failed", "deducted",
    "received"
}

CONDITIONAL_LOGISTICS_KEYWORDS = {"delay", "delayed"}

RECOMMENDATION_KEYWORDS = {
    "suggest", "recommend", "best for",
    "what should i use", "which product"
}

PERSONAL_CONTEXT_KEYWORDS = {
    "my skin", "my hair", "i have",
    "acne", "hair fall", "hairfall",
    "oily skin", "dry skin", "pigmentation"
}

ABOUT_PRODUCT_KEYWORDS = {
    "ingredients", "how to use", "usage",
    "apply", "price", "cost", "benefits",
    "safe", "side effects", "certified",
    "effective", "compare"
}

ABOUT_COMPANY_KEYWORDS = {
    "contact", "phone", "email",
    "team", "company",
    "customer care", "support"
}

def is_basic_interaction(text: str) -> bool:
    tokens = re.findall(r"\w+", text)
    if not tokens or len(tokens) > 4:
        return False
    return all(t in BASIC_INTERACTION_TOKENS for t in tokens)


def is_logistics_intent(text: str) -> bool:
    tokens = set(re.findall(r"\w+", text))

    if tokens & LOGISTICS_KEYWORDS:
        return True

    if tokens & CONDITIONAL_LOGISTICS_KEYWORDS:
        if tokens & {"order", "delivery", "shipment"}:
            return True

    return False


def is_recommendation_intent(text: str) -> bool:
    return (
        any(p in text for p in RECOMMENDATION_KEYWORDS) or
        any(p in text for p in PERSONAL_CONTEXT_KEYWORDS)
    )


def is_about_product_intent(text: str) -> bool:
    return any(p in text for p in ABOUT_PRODUCT_KEYWORDS)


def is_about_company_intent(text: str) -> bool:
    return any(p in text for p in ABOUT_COMPANY_KEYWORDS)


def detect_primary_intent(text: str) -> str:
    if is_basic_interaction(text):
        return "basic_interactions"

    if is_logistics_intent(text):
        return "logistics"

    if is_recommendation_intent(text):
        return "recommendation"

    if is_about_product_intent(text):
        return "about_product"

    if is_about_company_intent(text):
        return "about_company"

    return "flag"

ORDER_STATUS_KEYWORDS = {
    "track", "tracking", "status",
    "eta", "when", "dispatch",
    "shipped", "delay", "delayed"
}

REFUND_RETURN_KEYWORDS = {
    "refund", "return", "cancel",
    "money back", "damaged",
    "wrong product", "exchange"
}

DELIVERY_ISSUE_KEYWORDS = {
    "not received", "marked delivered",
    "delivered but not received",
    "rto", "returned to origin",
    "courier issue"
}


def detect_logistics_secondary(text: str) -> str:
    if any(k in text for k in DELIVERY_ISSUE_KEYWORDS):
        return "delivery_issue"

    if any(k in text for k in REFUND_RETURN_KEYWORDS):
        return "refund_return"

    if any(k in text for k in ORDER_STATUS_KEYWORDS):
        return "order_status"

    return "flag"


def detect_secondary_intent(primary: str, text: str) -> str:
    if primary == "logistics":
        return detect_logistics_secondary(text)
    return "flag"

if __name__ == "__main__":
    tests = [
        ("", "Hi"),
        ("", "Ok thanks"),
        ("", "How to track my order"),
        ("", "Refund ka status batao"),
        ("", "My order is delayed"),
        ("", "Marked delivered but not received"),
        ("", "Suggest something for hair growth"),
        ("", "How to use ABC face wash"),
        ("", "Contact number?")
    ]

    for history, msg in tests:
        text = build_text_for_analysis(history, msg)
        primary = detect_primary_intent(text)
        secondary = detect_secondary_intent(primary, text)
        print(f"\nMessage: {msg}")
        print("Primary:", primary)
        print("Secondary:", secondary)
