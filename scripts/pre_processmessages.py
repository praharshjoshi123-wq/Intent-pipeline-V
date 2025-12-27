import json

with open("data/raw_logs.json", "r", encoding="utf-8") as f:
    try:
        raw_logs = json.load(f)
    except json.JSONDecodeError as e:
        print("JSON ERROR →", e)
        raise

messages = []

for i, item in enumerate(raw_logs):
    messages.append({
        "message_id": f"msg_{i+1}",
        "text": item["current_human_message"]
    })

with open("data/messages.json", "w", encoding="utf-8") as f:
    json.dump(messages, f, indent=2, ensure_ascii=False)

print("messages.json created successfully")