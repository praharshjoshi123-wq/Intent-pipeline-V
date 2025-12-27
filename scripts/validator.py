import json

path = "data/raw_logs.json"

with open(path, "r", encoding="utf-8") as f:
    text = f.read()

try:
    json.loads(text)
    print("✅ JSON IS VALID")
except json.JSONDecodeError as e:
    print("❌ JSON IS INVALID")
    print(f"Message : {e.msg}")
    print(f"Line    : {e.lineno}")
    print(f"Column  : {e.colno}")
    print(f"Char pos: {e.pos}")