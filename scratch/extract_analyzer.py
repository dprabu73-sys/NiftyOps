import json
import re

def extract_analyzer():
    log_path = r"C:\Users\dprab\.gemini\antigravity\brain\b1af791f-03bb-4f39-89e4-6cb54cb4fc9f\.system_generated\logs\transcript_full.jsonl"
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        for idx, line in enumerate(f):
            if idx == 4612:
                try:
                    data = json.loads(line)
                    calls = data.get('tool_calls') or []
                    for c in calls:
                        args = c.get('arguments', {})
                        content = args.get('CodeContent') or args.get('ReplacementContent') or ''
                        if content:
                            print(f"Found content size: {len(content)}")
                            with open("templates/analyzer_original_recovered.html", "w", encoding="utf-8") as wf:
                                wf.write(content)
                            print("Saved to templates/analyzer_original_recovered.html")
                            return
                except Exception as e:
                    print("Error parsing line 4612:", e)

if __name__ == "__main__":
    extract_analyzer()
