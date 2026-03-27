# RentPulse Social Bot

## Stripe Webhook Setup (Render)

### 1. Deploy the webhook service on Render

Set the **Start Command** to:
```
python run_render_webhook.py
```

Render will automatically set the `PORT` env var. The server binds to `0.0.0.0:$PORT`.

---

### 2. Add env vars in Render dashboard

| Variable | Where to get it |
|---|---|
| `STRIPE_WEBHOOK_SECRET` | Stripe Dashboard → Developers → Webhooks → your endpoint → Signing secret |
| `STRIPE_SECRET_KEY` | Stripe Dashboard → Developers → API keys |

---

### 3. Register the endpoint in Stripe

In **Stripe Dashboard → Developers → Webhooks → Add endpoint**:

- **Endpoint URL**: `https://your-render-service.onrender.com/api/stripe/webhook`
- **Events to subscribe**: `checkout.session.completed` (only this one)

---

### 4. Local testing

Use the local webhook server (no signature verification, ngrok required):
```
python run_payment_webhook.py
```
Listens on port `8765` via `POST /webhook`.

---

### Files changed for Render support

| File | Change |
|---|---|
| `app/webhook/render_webhook.py` | New — Flask app with signature verification |
| `run_render_webhook.py` | New — Render entry point |
| `requirements.txt` | Added `flask==3.0.3` |
| `run_payment_webhook.py` | Unchanged — local testing |
| `app/webhook/stripe_webhook.py` | Unchanged — local testing |
| `app/agents/payment_handler.py` | Unchanged — shared logic |
