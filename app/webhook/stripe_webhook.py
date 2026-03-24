"""
Minimal Stripe webhook listener.

Starts a plain HTTP server (stdlib http.server) on a configurable port.
Accepts POST /webhook, parses the JSON body, and passes the event dict to
handle_payment_event() from app/agents/payment_handler.

NOTE: Stripe signature verification is not yet implemented.
      Run this behind a reverse proxy (e.g. ngrok) for local testing.

Usage (via run_payment_webhook.py):
    python run_payment_webhook.py
"""
import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

from app.agents.payment_handler import handle_payment_event

DEFAULT_PORT = 8765


class StripeWebhookHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        # Only handle /webhook path
        if self.path != "/webhook":
            self._respond(404, {"error": "not found"})
            return

        # Read body
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length)

        # Basic JSON check
        content_type = self.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            logging.warning("Non-JSON request received — rejecting")
            self._respond(400, {"error": "content-type must be application/json"})
            return

        # Parse JSON
        try:
            event = json.loads(raw_body)
        except json.JSONDecodeError as e:
            logging.warning(f"Invalid JSON body: {e}")
            self._respond(400, {"error": "invalid JSON"})
            return

        if not isinstance(event, dict):
            self._respond(400, {"error": "event must be a JSON object"})
            return

        # Hand off to payment handler
        summary = handle_payment_event(event)
        self._respond(200, summary)

    def _respond(self, status: int, body: dict) -> None:
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        # Route http.server access logs through Python logging
        logging.info(fmt % args)


def start_server(port: int = DEFAULT_PORT) -> None:
    """Start the webhook HTTP server (blocking)."""
    server = HTTPServer(("", port), StripeWebhookHandler)
    logging.info(f"Stripe webhook listener started on port {port}")
    logging.info("Waiting for POST /webhook ...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Webhook server stopped.")
    finally:
        server.server_close()
