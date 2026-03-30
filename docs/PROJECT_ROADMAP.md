# Project Roadmap

**Last updated:** 2026-03-30
**Project:** RentPulse Automation System
**Status:** Local build complete — pre-deployment

---

## SECTION 1: Project Overview

This system is a local automation assistant built around **RentPulse**, a Chrome extension for Irish rental market alerts. It handles four distinct workstreams from a single codebase:

- **RentPulse** — automated social media post generation and scheduling for platforms including Twitter/X, Threads, Bluesky, Reddit, Facebook, Instagram, TikTok, Indie Hackers, and Product Hunt
- **Job Hunter** — AI-powered job search agent that finds real active roles in Ireland, scores them for fit, and tracks applications through a full application lifecycle
- **Support** — Gmail-based support triage that classifies incoming emails by category, priority, and sentiment and saves structured tickets locally
- **Payments** — Stripe webhook listener that receives, validates, deduplicates, and stores payment events and customer records locally
- **Dashboard** — Local React dashboard (Vite + Express proxy) that surfaces all data across every subsystem in one place

---

## SECTION 2: Architecture

```
rentpulse-social-bot/
│
├── app/
│   ├── agents/              # Core agent logic
│   │   ├── job_hunter.py        — web search job finder + fit scorer
│   │   ├── job_tracker.py       — application tracker (status, shortlist, CV match)
│   │   ├── cv_profile.py        — candidate profile + local CV matching
│   │   ├── support_triage.py    — Gmail IMAP fetch + rule-based classifier
│   │   ├── payment_handler.py   — Stripe event parser + dispatcher
│   │   ├── payment_actions.py   — post-payment actions (notify, save customer)
│   │   └── customer_store.py    — adapter: maps payment record → storage interface
│   │
│   ├── content/             # Post generation
│   │   ├── generator.py         — Claude-powered social post generator
│   │   └── prompts.py           — system prompts per platform
│   │
│   ├── platforms/           # Platform posting clients
│   │   └── twitter.py, bluesky.py, reddit.py, facebook.py, linkedin.py, buffer.py
│   │
│   ├── research/            # Market research
│   │   └── market_analyser.py   — lead, competitor, complaint, content idea finder
│   │
│   ├── scheduler/           # Orchestration
│   │   ├── agent_scheduler.py   — runs agents on schedule
│   │   ├── notifier.py          — Telegram bot for approvals and alerts
│   │   └── timing.py            — posting schedule logic
│   │
│   ├── storage/             # Storage abstraction layer
│   │   ├── __init__.py          — public interface (4 functions)
│   │   ├── payments.py          — JSON implementation: save_payment, get_payments
│   │   └── customers.py         — JSON implementation: save_customer, get_customers
│   │
│   ├── utils/
│   │   ├── local_storage.py     — path constants + JSON/CSV helpers
│   │   └── logger.py
│   │
│   └── webhook/
│       ├── stripe_webhook.py    — FastAPI endpoint for Stripe events
│       └── render_webhook.py    — Render-compatible webhook listener
│
├── dashboard/
│   ├── server.cjs               — Express proxy + local data API
│   └── src/App.jsx              — React dashboard (Vite)
│
├── data/                    # All local data (JSON/CSV)
│   ├── jobs/                    — jobs.json, summary.json, job_applications.json
│   ├── payments/                — payment_events.json
│   ├── customers/               — customers.json
│   ├── support/                 — support_tickets.json
│   └── rentpulse/               — leads, complaints, competitors, content_ideas
│
└── docs/
    └── PROJECT_ROADMAP.md
```

### Data flow — payments

```
Stripe → webhook → payment_handler → app.storage.save_payment → data/payments/
                                   → payment_actions → customer_store → app.storage.save_customer → data/customers/
                                                     → Telegram notification
```

### Data flow — job hunt

```
run_job_hunt.py → job_hunter (Claude web search) → jobs.json + summary.json
                                                  → job_tracker.add_to_tracker (CV match)
                                                  → notify_new_jobs (Telegram, if configured)
```

---

## SECTION 3: Completed Work

### Infrastructure
- [x] Project structure and module layout
- [x] Local storage utilities (`local_storage.py` — path constants, JSON/CSV helpers)
- [x] `ensure_dirs()` — creates all data directories on startup
- [x] Telegram notifier (`notifier.py` — send, approval flow, edit, flush)

### Agents
- [x] **Job Hunter** — Claude web search, fit scoring, CSV + JSON output
- [x] **Job Tracker** — application lifecycle (saved → applied → interview → offer/rejected)
- [x] **CV Matcher** — local keyword-based match score, no API call required
- [x] **RentPulse Researcher** — leads, complaints, competitors, content ideas
- [x] **Support Triage** — Gmail IMAP fetch, rule-based + Claude fallback classification, deduplication by message ID

### Payments
- [x] Stripe webhook listener (local + Render-compatible)
- [x] Payment event parsing and type mapping
- [x] Deduplication by `session_id`
- [x] Skip invalid payments (no email)
- [x] Post-payment actions triggered on `checkout.session.completed`

### Customers
- [x] Customer record creation from payment event
- [x] Deduplication by email
- [x] Skip blank email

### Storage abstraction
- [x] `app/storage/` module created
- [x] `save_payment` / `get_payments` / `save_customer` / `get_customers` — clean interface
- [x] JSON backend isolated — agents no longer read/write files directly
- [x] `payment_handler.py` and `customer_store.py` refactored to use storage interface

### Dashboard
- [x] Express proxy server (`server.cjs`) with local data API
- [x] React dashboard (Vite)
- [x] **RentPulse tab** — social post generator (all 9 platforms), news check, post approval
- [x] **Research tab** — leads, complaints, competitors, content ideas
- [x] **Job Hunting tab** — job search results, best matches, applied tracker
- [x] **Application Tracker tab** — all/shortlisted/applied views, CV match score, status badges
- [x] **Payments tab** — payment events table
- [x] **Customers tab** — customer records table
- [x] **Support tab** — support tickets table

### CLI runners
- [x] `run_job_hunt.py` — trigger job search manually
- [x] `run_job_tracker.py` — import-jobs, list, shortlist, apply, status update
- [x] `run_support_triage.py` — trigger support email fetch manually

---

## SECTION 4: Current Position

The system is fully built and functional in local/build mode. Every subsystem — job hunting, support triage, payments, customer storage, social media automation, and the dashboard — is implemented and wired together. The storage layer has been abstracted so that swapping from JSON to a database requires changing two import lines. No automation is running: all agents are triggered manually via CLI runners, and no schedulers, triggers, or cron jobs are active. The system is ready for the next phase: connecting payments to user accounts, adding access control, and deploying to a persistent environment.

---

## SECTION 5: Next Steps

1. **Link payments to user accounts** — associate a `customer_id` or `email` with access permissions after a successful payment
2. **Premium gating** — restrict access to certain features (alerts, tracker, CV matching) based on payment status
3. **Database migration (Supabase)** — implement `app/storage/supabase_backend.py` with the same four function signatures and swap the import in `app/storage/__init__.py`
4. **`render.yaml`** — define services, environment variables, and build commands for Render deployment
5. **Production deployment** — deploy webhook listener and scheduler to Render; point Stripe webhook URL to live endpoint

---

## SECTION 6: Future Improvements

### Job tracking
- [ ] Browser-based status updates (mark applied/shortlisted from dashboard)
- [ ] Email reminders for stale applications
- [ ] Export tracker to CSV

### CV matching
- [ ] Richer profile configuration (upload actual CV text)
- [ ] Claude-powered deep match analysis (optional, on demand)
- [ ] Missing skill gap suggestions

### Alerts and notifications
- [ ] Telegram alert for new high-fit jobs (requires Telegram config)
- [ ] Alert when support ticket volume spikes
- [ ] Payment confirmation email to customer

### Social media
- [ ] Direct posting (currently copy-to-clipboard + open URL)
- [ ] Post history and analytics
- [ ] Per-platform scheduling with queue management

### Platform
- [ ] User authentication
- [ ] Multi-tenant support (multiple products beyond RentPulse)
- [ ] Admin dashboard view (metrics, health checks)
