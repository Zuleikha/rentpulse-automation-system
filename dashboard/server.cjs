const express = require("express");
const cors = require("cors");
const path = require("path");
const fs = require("fs");
const fetch = (...args) => import("node-fetch").then(({default: fetch}) => fetch(...args));
require("dotenv").config();

const app = express();
app.use(cors());
app.use(express.json());

// ---- Anthropic API proxy ----

app.post("/api/messages", async (req, res) => {
  try {
    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": process.env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "web-search-2025-03-05"
      },
      body: JSON.stringify(req.body)
    });
    const data = await response.json();
    res.json(data);
  } catch (err) {
    console.error("Error:", err.message);
    res.status(500).json({ error: err.message });
  }
});

// ---- Local data file helpers ----

const DATA_ROOT = path.join(__dirname, "..", "data");

function readJson(filePath) {
  try {
    const content = fs.readFileSync(filePath, "utf-8");
    return JSON.parse(content);
  } catch {
    return [];
  }
}

function readCsv(filePath) {
  try {
    const content = fs.readFileSync(filePath, "utf-8").trim();
    if (!content) return [];
    const lines = content.split("\n").filter(Boolean);
    if (lines.length < 2) return [];
    const headers = lines[0].split(",").map(h => h.trim().replace(/^"|"$/g, ""));
    return lines.slice(1).map(line => {
      const values = line.split(",").map(v => v.trim().replace(/^"|"$/g, ""));
      const obj = {};
      headers.forEach((h, i) => { obj[h] = values[i] || ""; });
      return obj;
    });
  } catch {
    return [];
  }
}

// ---- Jobs data endpoint ----

app.get("/api/data/jobs/tracker", (req, res) => {
  const all = readJson(path.join(DATA_ROOT, "jobs", "job_applications.json"));
  const list = Array.isArray(all) ? all : [];
  res.json({
    all:         list,
    shortlisted: list.filter(j => j.shortlisted),
    applied:     list.filter(j => ["applied", "interview", "offer"].includes(j.status)),
  });
});

app.get("/api/data/jobs", (req, res) => {
  const dir = path.join(DATA_ROOT, "jobs");
  res.json({
    jobs:        readJson(path.join(dir, "jobs.json")),
    summary:     readJson(path.join(dir, "summary.json")),
    job_tracker: readJson(path.join(dir, "job_tracker.json")),
  });
});

// ---- RentPulse research data endpoint ----

app.get("/api/data/rentpulse", (req, res) => {
  const dir = path.join(DATA_ROOT, "rentpulse");
  res.json({
    leads:         readJson(path.join(dir, "leads.json")),
    complaints:    readJson(path.join(dir, "complaints.json")),
    competitors:   readJson(path.join(dir, "competitors.json")),
    content_ideas: readJson(path.join(dir, "content_ideas.json")),
  });
});

// ---- Payments data endpoint ----

app.get("/api/data/payments", (req, res) => {
  const events = readJson(path.join(DATA_ROOT, "payments", "payment_events.json"));
  const payments = events
    .filter(e => e.type === "payment_success")
    .map(e => ({
      email:      e.customer_email || "",
      amount:     e.amount,
      timestamp:  e.received_at || "",
      session_id: e.id || "",
    }));
  res.json({ payments });
});

// ---- Customers data endpoint ----

app.get("/api/data/customers", (req, res) => {
  const customers = readJson(path.join(DATA_ROOT, "customers", "customers.json"));
  res.json({ customers });
});

// ---- Support tickets data endpoint ----

app.get("/api/data/support", (req, res) => {
  const tickets = readJson(path.join(DATA_ROOT, "support", "support_tickets.json"));
  res.json({ tickets });
});

app.listen(3001, () => console.log("Proxy running on port 3001"));
