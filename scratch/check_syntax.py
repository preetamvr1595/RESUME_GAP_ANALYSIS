
import re

with open(r'e:\RESUME_GAP_ANALYSIS_NEW\RESUME-GAP-AI\skillforge_frontend.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract script content
script_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
if script_match:
    script_content = script_match.group(1)
    # Save to a temp file for syntax check
    with open('temp_script.js', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # We can try to use node or just a simple check
    print("Extracted script for checking.")
else:
    print("No script tag found.")
