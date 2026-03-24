import json
from pathlib import Path
from datetime import datetime
import subprocess

output = Path(r"D:\rentfast\IrelandRentPulse\rentpulse-social-bot\data\jobs\jobs.json")

prompt = """
Search for job listings posted in the last 24 hours.

Roles:
- AI Engineer
- Machine Learning Engineer
- AI Research Engineer
- Backend Engineer (AI/data focus)
- MLOps Engineer
- Data Engineer (ML focus)
- Bioinformatics / Computational Biology

Filters:
- Location: Ireland, UK, Europe
- Include Remote, Hybrid, Onsite
- Salary: €80,000+
- Mid-level roles

Return JSON list with:
- title
- company
- location
- salary
- link
- summary
"""

result = subprocess.run(
    [r"C:\ProgramData\anaconda3\python.exe", "-m", "openclaw"],
    input=prompt,
    text=True,
    capture_output=True
)

print("STDOUT:")
print(result.stdout)
print("STDERR:")
print(result.stderr)

try:
    jobs = json.loads(result.stdout)
except:
    jobs = []

output.parent.mkdir(parents=True, exist_ok=True)
with output.open("w", encoding="utf-8") as f:
    json.dump(jobs, f, indent=2)

print("Jobs updated")
