import json

with open("data/raw_logs.json", "r") as f:
    raw_logs = json.load(f)

messages = []

for i, item in enumerate(raw_logs):
    messages.append({
        "message_id": f"msg_{i+1}",
        "text": item["current_human_message"]
    })

with open("data/messages.json", "w") as f:
    json.dump(messages, f, indent=2)