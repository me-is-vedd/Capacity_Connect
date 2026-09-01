import re

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Remove non-ASCII
    line = re.sub(r'[^\x00-\x7F]+', '', line)
    # Fix spaces at start of quotes
    line = re.sub(r'([\'"])\s+', r'\1', line)
    # Fix spaces at end of quotes
    line = re.sub(r'\s+([\'"])', r'\1', line)
    new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Emojis stripped.")
