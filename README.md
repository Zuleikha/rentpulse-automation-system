# RentPulse Social Bot

Automation system for RentPulse. Handles social media content generation, market research, payment processing, user accounts, and support triage. Runs locally with a React dashboard.

---

## What is in this repo

| Module | What it does |
|---|---|
| `app/agents/` | Core agents: research, content, job hunting, payments, users, scam detection |
| `app/access/` | Premium access gate — `is_premium_user(email)`, `require_premium(email)` |
| `app/content/` | Claude-powered post generator and platform prompt templates |
| `app/platforms/` | Social platform API integrations (Twitter, Reddit, Bluesky, LinkedIn, etc.) |
| `app/scheduler/` | Schedule library wrapper, Telegram approval flow, timing helpers |
| `app/storage/` | JSON-backed storage for payments, customers, users |
| `app/utils/` | Config, logger, local file utilities |
| `app/webhook/` | Stripe webhook (local + Render/production) |
| `dashboard/` | React + Vite dashboard, Express proxy server at port 3001 |

---

## Current project status

**Stage 8 (premium gating) is implemented.** See `docs/PROJECT_ROADMAP.md` for full stage history.

| Area | Status |
|---|---|
| Social post generation | Done |
| Market research (leads, complaints, competitors, content ideas) | Done |
| Job hunter + application tracker | Done |
| Stripe webhook (local + Render) | Done |
| Payment processing + customer storage | Done |
| User account model + payment linking | Done |
| Premium access gate | Done (scaffold — local storage, no Stripe dependency) |
| Database migration (Supabase) | Not started |
| Production deployment | Not started |

---

## Premium gating

Premium status is stored locally in `data/users/users.json`. It is set automatically when a successful Stripe payment is processed via `user_linker.link_payment_to_user()`.

**Gated features:**
- Research tasks: `leads` and `competitors` (premium only when called with a user email)
- Scam detection: `app/agents/scam_detector.py` (premium only — detection logic is a TODO stub)

**Free features remain fully accessible:**
- Research tasks: `content_ideas` and `complaints`
- Social post generation
- All dashboard sections

**To toggle gating:**
```
PREMIUM_ENABLED=false   # disable gate — treat all users as premium
PREMIUM_ENABLED=true    # default — check user record
```

**To grant premium locally for testing:**
```bash
python -c "
from app.agents.user_linker import create_user_if_missing, link_payment_to_user
create_user_if_missing('you@example.com')
link_payment_to_user('test_session_01', 'you@example.com')
print('Done')
"
```

---

## Setup

### Python backend

```bash
pip install -r requirements.txt
cp .env.example .env
# fill in ANTHROPIC_API_KEY and any platform tokens you need
```

### Dashboard

```bash
cd dashboard
npm install
node server.cjs        # Express proxy — port 3001
npm run dev            # Vite dev server — port 5173
```

---

## Running agents manually

```bash
python run_rentpulse_research.py   # market research (web search)
python run_job_hunt.py             # job search (web search)
python run_job_tracker.py          # update application tracker
python run_support_triage.py       # triage Gmail support inbox
python run_scheduler.py            # start the automated scheduler loop
```

---

## Stripe webhook

### Production (Render)

Set the start command to:
```
python run_render_webhook.py
```

Render sets `PORT` automatically. Add these env vars in the Render dashboard:

| Variable | Where to get it |
|---|---|
| `STRIPE_WEBHOOK_SECRET` | Stripe Dashboard → Developers → Webhooks → signing secret |
| `STRIPE_SECRET_KEY` | Stripe Dashboard → Developers → API keys |

Register endpoint in Stripe: `https://your-render-service.onrender.com/api/stripe/webhook`
Subscribe to event: `checkout.session.completed`

### Local testing

```bash
python run_payment_webhook.py   # listens on port 8765, POST /webhook
```

---

## Dashboard sections

| Tab | What it shows |
|---|---|
| RentPulse | Social post generator + research results (leads, complaints, competitors, content ideas) |
| Job Hunting | Job search results + application tracker |
| Payments | Payment events from Stripe |
| Customers | Customer records (deduplicated by email) |
| Support | Support ticket triage results |
| Run Controls | Trigger and monitor agent runs |
| Users | User accounts, premium status, linked payment sessions |

---

## Next steps

1. Database migration — move storage from local JSON to Supabase
2. `render.yaml` — define all Render services in one file
3. Production deployment — push to Render, verify webhook end-to-end
