import re

with open("templates/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Match simple fetch patterns
matches = re.findall(r'fetch\([\'"]([^\'"]+)[\'"]', content)
print("Fetch endpoints:")
for m in sorted(list(set(matches))):
    print("  ", m)
