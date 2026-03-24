import json
from pathlib import Path

output = Path(r"D:\rentfast\IrelandRentPulse\rentpulse-social-bot\data\jobs\jobs.json")

jobs = [
    {
        "title": "AI Engineer",
        "company": "Example Company",
        "location": "Dublin / Hybrid",
        "salary": "€80,000+",
        "link": "https://example.com/job",
        "summary": "Strong fit for transition into AI/ML from software development.",
        "status": "Not Applied"
    }
]

output.parent.mkdir(parents=True, exist_ok=True)
with output.open("w", encoding="utf-8") as f:
    json.dump(jobs, f, indent=2)

print(f"Wrote {output}")
