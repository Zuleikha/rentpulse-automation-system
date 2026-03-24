"""
CLI entry point: run all RentPulse research tasks.

Usage:
    python run_rentpulse_research.py              # run all tasks
    python run_rentpulse_research.py leads        # run one task
    python run_rentpulse_research.py complaints
    python run_rentpulse_research.py competitors
    python run_rentpulse_research.py content_ideas

Saves results to:
    data/rentpulse/leads.json
    data/rentpulse/complaints.json
    data/rentpulse/competitors.json
    data/rentpulse/content_ideas.json
"""
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    from app.agents.rentpulse_researcher import run_all_research, run_research_task, RESEARCH_TASKS

    args = sys.argv[1:]

    if args:
        task_name = args[0].strip()
        if task_name not in RESEARCH_TASKS:
            print(f"Unknown task: {task_name}")
            print(f"Available tasks: {', '.join(RESEARCH_TASKS.keys())}")
            sys.exit(1)
        results = run_research_task(task_name)
        print(f"\n=== {task_name} complete: {len(results)} results ===")
    else:
        results = run_all_research()
        print("\n=== RentPulse Research Complete ===")
        for task, items in results.items():
            print(f"  {task:20s}: {len(items)} results")

    print("\nResults saved to data/rentpulse/")
