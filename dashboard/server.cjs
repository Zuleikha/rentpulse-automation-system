const express = require("express");
const cors = require("cors");
const path = require("path");
const fs = require("fs");
const { spawn } = require("child_process");
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
const PROJECT_ROOT = path.join(__dirname, "..");
const RUNS_FILE = path.join(DATA_ROOT, "runs", "run_log.json");

// ---- Run log helpers ----

function readRunLog() {
  try {
    if (!fs.existsSync(RUNS_FILE)) return {};
    return JSON.parse(fs.readFileSync(RUNS_FILE, "utf-8"));
  } catch { return {}; }
}

function setRunStatus(project, fields) {
  const dir = path.dirname(RUNS_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  const log = readRunLog();
  log[project] = { project, ...fields };
  fs.writeFileSync(RUNS_FILE, JSON.stringify(log, null, 2));
}

// ---- Run script helper ----
// Spawns a Python runner, writes status to run_log.json, returns a Promise.

function runScript(project, script) {
  return new Promise((resolve) => {
    const started_at = new Date().toISOString();
    setRunStatus(project, { started_at, finished_at: null, status: "running", message: "" });
    console.log(`[run] starting ${project} (${script})`);

    const proc = spawn("python", [script], {
      cwd: PROJECT_ROOT,
      env: { ...process.env },
      shell: false,
    });

    let out = "";
    let err = "";
    proc.stdout.on("data", (d) => { out += d.toString(); });
    proc.stderr.on("data", (d) => { err += d.toString(); });

    proc.on("close", (code) => {
      const finished_at = new Date().toISOString();
      const status = code === 0 ? "success" : "failed";
      const combined = (out + "\n" + err).trim();
      const message = combined.slice(-500).trim();
      setRunStatus(project, { started_at, finished_at, status, message });
      console.log(`[run] ${project} → ${status} (exit ${code})`);
      resolve({ project, status, code });
    });

    proc.on("error", (e) => {
      const finished_at = new Date().toISOString();
      setRunStatus(project, { started_at, finished_at, status: "failed", message: e.message });
      console.error(`[run] ${project} spawn error:`, e.message);
      resolve({ project, status: "failed", code: -1 });
    });
  });
}

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

// ---- Run control routes ----
// Each route responds immediately (started: true) then runs the agent in the
// background. Poll GET /api/data/runs to check current status.

app.post("/api/run/rentpulse", (req, res) => {
  res.json({ started: true, project: "rentpulse" });
  runScript("rentpulse", "run_rentpulse_research.py");
});

app.post("/api/run/job-hunt", (req, res) => {
  res.json({ started: true, project: "job-hunt" });
  runScript("job-hunt", "run_job_hunt.py");
});

app.post("/api/run/support", (req, res) => {
  res.json({ started: true, project: "support" });
  runScript("support", "run_support_triage.py");
});

app.post("/api/run/all", async (req, res) => {
  res.json({ started: true, project: "all" });
  // Sequential: each agent waits for the previous to finish.
  await runScript("rentpulse", "run_rentpulse_research.py");
  await runScript("job-hunt", "run_job_hunt.py");
  await runScript("support", "run_support_triage.py");
});

// ---- Run status endpoint ----

app.get("/api/data/runs", (req, res) => {
  res.json(readRunLog());
});

app.listen(3001, () => console.log("Proxy running on port 3001"));
