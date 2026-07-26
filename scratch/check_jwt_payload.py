import os, json, base64

env_path = r"c:\Users\dprab\OneDrive\Desktop\Tradingview\Prabu New Trading view\.env"
with open(env_path) as f:
    for line in f:
        if line.startswith("TV_JWT_TOKEN="):
            jwt = line.split("=", 1)[1].strip()
            parts = jwt.split(".")
            padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
            payload = json.loads(base64.urlsafe_b64decode(padded))
            print("Full JWT Payload:")
            print(json.dumps(payload, indent=2))
