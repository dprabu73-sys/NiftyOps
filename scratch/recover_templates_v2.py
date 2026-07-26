import os
import glob
import json
import re

def recover_files():
    brain_dir = os.path.expanduser(r'~\.gemini\antigravity\brain')
    logs = glob.glob(os.path.join(brain_dir, '*', '.system_generated', 'logs', 'transcript_full.jsonl'))

    print(f"Scanning {len(logs)} logs...")
    for log_path in logs:
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                for idx, line in enumerate(f):
                    if '<!DOCTYPE html>' in line:
                        try:
                            data = json.loads(line)
                            content = data.get('content') or ''
                            
                            # Check tool_calls with both keys: arguments and args
                            if 'tool_calls' in data:
                                for c in data['tool_calls']:
                                    args = c.get('args') or c.get('arguments') or {}
                                    content += args.get('CodeContent', '') + args.get('ReplacementContent', '')
                            
                            if content:
                                m = re.search(r'(<!DOCTYPE html>.*?</html>)', content, re.DOTALL | re.IGNORECASE)
                                if m:
                                    html = m.group(1)
                                    titles = re.findall(r'<title>(.*?)</title>', html, re.IGNORECASE)
                                    if titles:
                                        title = titles[0]
                                        print(f"Match: {log_path} Line {idx} Title: {title} Size: {len(html)}")
                                        
                                        # Save to templates folder with unique name
                                        clean_title = "".join(x for x in title if x.isalnum() or x in " -_").strip()
                                        out_path = f"templates/recovered_{clean_title}_{idx}.html"
                                        with open(out_path, 'w', encoding='utf-8') as wf:
                                            wf.write(html)
                                        print(f"  Saved to {out_path}")
                        except Exception as json_err:
                            pass
        except Exception as e:
            print(f"Error reading {log_path}: {e}")

if __name__ == "__main__":
    recover_files()
