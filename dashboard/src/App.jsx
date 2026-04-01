import { useState, useEffect } from "react";

// ============================================================
// SCHEDULE & CONSTANTS  (unchanged from original)
// ============================================================

const SCHEDULE = [
  { platform: "Twitter/X", handle: "@rentpulse", days: [0, 1, 2, 3, 4, 5, 6], color: "#1d9bf0", url: "https://twitter.com/compose/tweet" },
  { platform: "Threads", handle: "@rentpulse.ie", days: [0, 1, 2, 3, 4, 5, 6], color: "#000", url: "https://www.threads.net/intent/post" },
  { platform: "Facebook", handle: "RentPulse", days: [1, 3, 5], color: "#1877f2", url: "https://www.facebook.com/?id=61584297453610" },
  { platform: "Instagram", handle: "rentpulse.ie", days: [1, 4], color: "#e1306c", url: "https://www.instagram.com/rentpulse.ie" },
  { platform: "TikTok", handle: "rentpulse.ie", days: [2, 5], color: "#010101", url: "https://www.tiktok.com/upload" },
  { platform: "Reddit", handle: "r/ireland • r/dublin • r/irishpersonalfinance • r/DublinHousing", days: [1, 4], color: "#ff4500", url: "https://www.reddit.com/r/ireland/submit" },
  { platform: "Indie Hackers", handle: "indiehackers.com", days: [3], color: "#0e7f6c", url: "https://www.indiehackers.com/post" },
  { platform: "Product Hunt", handle: "rentpulse", days: [0], color: "#da552f", url: "https://www.producthunt.com/posts/rentpulse" },
  { platform: "Bluesky", handle: "rentpulse.bsky.social", days: [1, 3, 5], color: "#0085ff", url: "https://bsky.app/intent/compose" },
];

const DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const FULL_DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

const POST_ANGLES = [
  "speed_of_listings", "rental_competition", "renters_refreshing_pages",
  "missing_listings_by_minutes", "timing_matters_in_renting",
  "small_tools_that_help_renters", "observing_the_rental_market",
  "trying_to_be_first_to_apply", "renting_feels_like_a_second_job",
  "builder_solving_a_small_problem",
];

const POST_HOOKS = [
  "Most rental listings are gone before people even see them.",
  "Renting in Ireland has become a timing game.",
  "Missing a listing by 10 minutes can mean missing it completely.",
  "For a lot of renters, checking listings has become a second job.",
  "The hardest part of renting is often just seeing a place in time.",
  "A good rental can disappear faster than most people can react.",
  "In renting, speed matters more than ever.",
  "A lot of renters are not too late because they are careless. They are too late because the process is broken.",
  "The window to catch a decent rental is often tiny.",
  "The difference between seeing a listing early and late is everything.",
  "Checking one site is not enough anymore.",
  "New rentals appear across multiple sites at once — most people only watch one.",
  "The listings that disappear fastest are the ones spread across different rental sites.",
];

const TOPIC_POOL = [
  "renters missing listings by minutes",
  "good rentals disappearing too fast",
  "refreshing pages constantly to catch something early",
  "timing matters more than ever in renting",
  "renting feels like a second job",
  "competition for rental listings is intense",
  "being early is often the only advantage renters have",
  "new listings appearing across multiple rental sites at once",
  "missing a listing because you were only watching one site",
  "having to check multiple sites manually every day",
];

const SOFT_CTA_STYLES = [
  "mention_the_tool_casually", "end_with_a_quiet_recommendation",
  "frame_it_as_something_helpful_you_built",
  "mention_it_like_a_useful_tip", "refer_to_it_as_a_small_tool_not_a_product",
];

const AVOID_PHRASES = [
  "game changer", "check it out", "sign up now", "do not miss out",
  "perfect for renters", "revolutionising renting", "super useful",
  "must-have tool", "free chrome extension for renters", "built to help renters",
  "in today's competitive market", "navigating the rental landscape",
  "designed for", "seamlessly", "empowering renters", "stay ahead",
  "never miss a listing", "rental journey", "streamline", "peace of mind",
  "level the playing field", "at your fingertips",
];

const HASHTAG_POOLS = {
  "Twitter/X": ["#RentingIreland", "#HousingIreland", "#DublinRent"],
  "Threads": ["#RentingIreland", "#HousingIreland"],
  "Facebook": [],
  "Instagram": ["#RentingIreland", "#DublinRent", "#HousingIreland", "#IrishHousing"],
  "TikTok": ["#RentingIreland", "#HousingIreland", "#DublinRent"],
  "Reddit": [], "Indie Hackers": [], "Product Hunt": [],
  "Bluesky": ["#RentingIreland", "#HousingIreland"],
};

const PLATFORM_TONES = {
  "Twitter/X": "Write a short X post. Tone: punchy, direct, natural. Keep it tight. Prefer 140-190 characters when possible. Hashtags only if they fit naturally.",
  "Threads": "Write a short Threads post. Tone: conversational, relatable, slightly reflective. Make it feel like a real person posting, not a brand.",
  "Facebook": "Write a short Facebook post. Tone: community-based, useful, informal. 2-3 short paragraphs max. Make it feel like a real person sharing a tip or observation.",
  "Instagram": "Write a short Instagram caption. Tone: relatable and scroll-stopping but still natural. Use short lines. Add hashtags only at the end if they fit naturally.",
  "TikTok": "Write a short TikTok caption. Tone: sharp, short, direct. Keep it concise and easy to pair with a demo video.",
  "Reddit": "Write a Reddit-style post. Tone: brutally honest, grounded, zero marketing language. This community is highly sensitive to self-promotion — the post must read like a genuine observation or tip from a renter or builder, not a product announcement. Only mention RentPulse in the final sentence if it fits naturally, and even then keep it low-key. The subreddit for this post will be specified in the prompt — tailor the voice and angle to that community.",
  "Indie Hackers": "Write a short founder-style post for Indie Hackers. Tone: thoughtful, honest, builder-focused. This audience is skeptical of marketing — they respect real numbers, honest reflections, and genuine problem-solving. Talk about the problem you observed and what you built to solve it. If you have a specific metric (users, alerts sent, installs), mention it — it adds credibility. Do not pitch. Do not hype.",
  "Product Hunt": "Write a short Product Hunt update. Tone: calm, clear, grateful, product-focused. Speak directly to the Product Hunt community — acknowledge their support, share a genuine insight or milestone, keep it grounded. No hype, no hard sell. One specific detail (a user story, a number, a feature) makes it feel real.",
  "Bluesky": "Write a short Bluesky post. Tone: casual, observational, slightly warmer than X, conversation-friendly.",
};

const REDDIT_SUBREDDITS = [
  { name: "r/ireland", note: "General Irish audience. Keep it observational and relatable. Avoid anything that feels like marketing." },
  { name: "r/dublin", note: "Dublin-focused renters. Hyper-local angle works well. Real frustrations about the Dublin market land better than general points." },
  { name: "r/irishpersonalfinance", note: "Financially-minded audience. Practical, data-driven tone works here. Frame around saving time or being more efficient as a renter." },
  { name: "r/DublinHousing", note: "Renters actively struggling with Dublin housing. Empathetic, grounded tone. Speak to the pain of the search, not the solution." },
];

const MEDIA_GUIDANCE = {
  "Twitter/X": "Use video sometimes, not often. Prefer text by default. Use screenshot occasionally.",
  "Threads": "Use text by default. Use video when showing how the tool works. Screenshot is also fine.",
  "Facebook": "Prefer text or screenshot. Use video sparingly.",
  "Instagram": "Video and screenshot both fit. Use video when the post is about how the tool works.",
  "TikTok": "Video is a strong fit when the post is about speed, alerts, or how the extension works.",
  "Reddit": "Prefer text only. Avoid promo-style media.",
  "Indie Hackers": "Prefer text or screenshot. Video only if genuinely useful.",
  "Product Hunt": "Prefer screenshot or short product demo when relevant.",
  "Bluesky": "Prefer text. Use video occasionally, not every time.",
};

const NEWS_SYSTEM = `You monitor Irish rental market news for RentPulse, a Chrome extension for Irish rental alerts.
Search for anything newsworthy in the last 48 hours: rent price changes, new housing reports, government policy, data, housing crisis developments.
Return ONLY a JSON object, no markdown, no preamble:
{"hasNews":true,"headline":"short headline","summary":"2 sentence summary","urgency":"high/medium/low"}
If no news found return exactly: {"hasNews":false,"headline":"","summary":"","urgency":""}`;

const API = "http://localhost:3001/api/messages";
const DATA_API = "http://localhost:3001/api/data";
const RUN_API = "http://localhost:3001/api/run";
const RECENT_POSTS_STORAGE_KEY = "rp_recent_posts_v3";
const MAX_RECENT_POSTS = 20;

// ============================================================
// UTILITY FUNCTIONS  (unchanged from original)
// ============================================================

function pickRandom(list) {
  return list[Math.floor(Math.random() * list.length)];
}
function getTopic() { return pickRandom(TOPIC_POOL); }
function getPostAngle() { return pickRandom(POST_ANGLES); }
function getPostHook() { return pickRandom(POST_HOOKS); }
function getSoftCtaStyle() { return pickRandom(SOFT_CTA_STYLES); }

function getPlatformHashtags(platform, maxTags = 2) {
  const tags = HASHTAG_POOLS[platform] || [];
  if (!tags.length) return [];
  const shuffled = [...tags].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, Math.min(maxTags, tags.length));
}

function loadRecentPostsMap() {
  try { return JSON.parse(localStorage.getItem(RECENT_POSTS_STORAGE_KEY) || "{}"); }
  catch { return {}; }
}
function loadRecentPosts(platform) {
  const all = loadRecentPostsMap();
  return Array.isArray(all[platform]) ? all[platform] : [];
}
function saveRecentPost(platform, content) {
  if (!content || !content.trim()) return;
  try {
    const all = loadRecentPostsMap();
    const existing = Array.isArray(all[platform]) ? all[platform] : [];
    const updated = [...existing, content.trim()].slice(-MAX_RECENT_POSTS);
    all[platform] = updated;
    localStorage.setItem(RECENT_POSTS_STORAGE_KEY, JSON.stringify(all));
  } catch {}
}
function buildRecentPostsInstruction(recentPosts = []) {
  const cleaned = recentPosts.map((p) => String(p || "").trim()).filter(Boolean);
  if (!cleaned.length) return "";
  return `Avoid repeating ideas or phrasing from these recent posts: ${cleaned.slice(-5).join(" || ")}. `;
}
function buildAvoidPhrasesInstruction() {
  return `Do not use these phrases: ${AVOID_PHRASES.map((p) => `'${p}'`).join(", ")}. `;
}
function buildUserPrompt(platform, context = "", recentPosts = []) {
  const angle = getPostAngle();
  const hook = getPostHook();
  const ctaStyle = getSoftCtaStyle();
  const topic = getTopic();
  const hashtags = getPlatformHashtags(platform);
  const MAX_LENGTH = {
    "Twitter/X": 170, "Threads": 260, "Facebook": 200, "Instagram": 240,
    "TikTok": 130, "Reddit": 260, "Indie Hackers": 260, "Product Hunt": 220, "Bluesky": 170
  };
  const maxChars = MAX_LENGTH[platform] || 300;
  const hashtagText = hashtags.length ? hashtags.join(" ") : "none";
  const contextInstruction = context ? `There is relevant Irish rental market news today — use it as context to make the post timely and grounded, but do not summarise the news directly: ${context} ` : "";
  const recentInstruction = buildRecentPostsInstruction(recentPosts);
  const avoidPhrasesInstruction = buildAvoidPhrasesInstruction();
  const redditSubreddit = platform === "Reddit" ? pickRandom(REDDIT_SUBREDDITS) : null;
  const redditInstruction = redditSubreddit
    ? `This post is for ${redditSubreddit.name}. ${redditSubreddit.note} In the 'note' field, return: "Post to ${redditSubreddit.name}". `
    : "";
  const noteInstruction = platform !== "Reddit"
    ? `In the 'note' field, return one specific, actionable posting tip for ${platform} — not generic advice. `
    : "";
  return (
    `${contextInstruction}${recentInstruction}${avoidPhrasesInstruction}` +
    `Write one post for ${platform}. ` +
    `The final post MUST be under ${maxChars} characters. ` +
    `Never produce a thread. Only one post. ` +
    `Before returning, count the characters in your post. If it is over ${maxChars}, shorten it and count again. Do not return a post that exceeds ${maxChars} characters. ` +
    `Focus on this angle: ${angle}. ` +
    `Use this renter discussion topic as background context: '${topic}'. ` +
    `Draw inspiration from this hook for your opening but do not copy it — find your own angle and wording: '${hook}'. ` +
    `Use this ending style: ${ctaStyle}. ` +
    `Mention RentPulse naturally as a Chrome extension that searches multiple rental sites and sends instant desktop alerts when new listings appear. Emphasise that it covers all rental types including house shares and student accommodation. ` +
    `Do not sound like advertising. No emojis. No hype. No sales language. ` +
    `Do not name specific rental sites. Refer to them only as "multiple rental sites" or "rental sites". Write like a real person. ` +
    `Prefer 140–180 characters for Twitter and Bluesky when possible. ` +
    `Vary wording, rhythm, and sentence openings. Avoid generic AI-sounding phrases. ` +
    `Prefer shorter posts. If unsure, make it shorter. Avoid long explanations. ` +
    `For the postType field: choose 'video' only when the post is explicitly about speed, alerts firing, or how the extension works in real time — not just because it mentions RentPulse. Most posts should be 'text'. ` +
    `For the useDemoVideo field: set to true only when postType is 'video'. Otherwise set to false. ` +
    `${redditInstruction}${noteInstruction}` +
    `If hashtags are used, only use these and only if they fit naturally: ${hashtagText}.`
  );
}

const SYSTEM_PROMPT = (platform) => `You are a social media content writer for RentPulse.
RentPulse is a Chrome extension that searches multiple rental sites and sends instant desktop alerts for new Irish rental listings, covering all rental types including house shares and student accommodation.
Audience: Irish renters aged 22-40 living in or moving to Dublin, Cork, Galway, or other Irish cities.
The posts must feel native to the platform, human, grounded, and specific to renting in Ireland.
Do not write like an advertiser, brand marketer, or growth hacker.
Never use emojis. Never name specific rental sites.
Never use hype, hard sell, pushy CTA language, or obvious ad copy.
Platform instructions for ${platform}: ${PLATFORM_TONES[platform]}
postType must be exactly one of: text, screenshot, video. useDemoVideo must be true only when postType is video, otherwise false. note must be one specific actionable tip for this post — not generic advice.
Return ONLY a valid JSON object with no markdown, no preamble, no trailing text:
{"content":"post text here","note":"one specific actionable posting tip","postType":"text","useDemoVideo":false}`;

function getPostTypeLabel(postType) {
  if (postType === "video") return "Video post";
  if (postType === "screenshot") return "Screenshot post";
  return "Text post";
}
function getPostTypeColors(postType) {
  if (postType === "video") return { bg: "#ecfeff", border: "#a5f3fc", text: "#0f766e" };
  if (postType === "screenshot") return { bg: "#eff6ff", border: "#bfdbfe", text: "#1d4ed8" };
  return { bg: "#f8fafc", border: "#e2e8f0", text: "#475569" };
}

// ============================================================
// UI HELPERS
// ============================================================

function sectionTabStyle(active) {
  return {
    padding: "8px 22px", borderRadius: 6, fontWeight: 700, fontSize: 14, cursor: "pointer",
    border: active ? "none" : "1.5px solid #e2e8f0",
    background: active ? "#1e40af" : "#fff",
    color: active ? "#fff" : "#374151",
  };
}
function subTabStyle(active) {
  return {
    padding: "6px 16px", borderRadius: 6, fontWeight: 600, fontSize: 13, cursor: "pointer",
    border: active ? "none" : "1.5px solid #e2e8f0",
    background: active ? "#2563eb" : "#f8fafc",
    color: active ? "#fff" : "#374151",
  };
}

function PanelCard({ title, count, children }) {
  return (
    <div style={{ border: "1.5px solid #e2e8f0", borderRadius: 8, marginBottom: 16, overflow: "hidden" }}>
      <div style={{ background: "#f8fafc", borderBottom: "1px solid #e2e8f0", padding: "10px 16px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span style={{ fontWeight: 700, fontSize: 13, color: "#374151" }}>{title}</span>
        {count !== undefined && (
          <span style={{ fontSize: 12, color: "#64748b", background: "#e2e8f0", padding: "2px 8px", borderRadius: 99 }}>{count}</span>
        )}
      </div>
      <div style={{ padding: 16 }}>{children}</div>
    </div>
  );
}

function EmptyState({ message, command }) {
  return (
    <div style={{ textAlign: "center", padding: "36px 24px", color: "#64748b" }}>
      <div style={{ fontSize: 14, marginBottom: 10 }}>{message}</div>
      {command && (
        <code style={{ background: "#f1f5f9", color: "#1e293b", padding: "5px 12px", borderRadius: 4, fontSize: 12, display: "inline-block" }}>
          {command}
        </code>
      )}
    </div>
  );
}

function UrgencyBadge({ urgency }) {
  const colors = {
    high:   { bg: "#fee2e2", text: "#dc2626" },
    medium: { bg: "#fef3c7", text: "#d97706" },
    low:    { bg: "#e0f2fe", text: "#0369a1" },
  };
  const c = colors[(urgency || "").toLowerCase()] || colors.low;
  return (
    <span style={{ background: c.bg, color: c.text, fontSize: 11, fontWeight: 700, padding: "2px 8px", borderRadius: 99, textTransform: "uppercase" }}>
      {urgency || "low"}
    </span>
  );
}

function FitBadge({ score }) {
  const n = Number(score) || 0;
  const bg   = n >= 8 ? "#dcfce7" : n >= 6 ? "#fef9c3" : "#fee2e2";
  const text = n >= 8 ? "#15803d" : n >= 6 ? "#a16207" : "#b91c1c";
  return (
    <span style={{ background: bg, color: text, fontSize: 12, fontWeight: 700, padding: "2px 10px", borderRadius: 99 }}>
      {n}/10
    </span>
  );
}

function DataRefreshBar({ loading, onRefresh, lastKey }) {
  return (
    <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 12 }}>
      <button
        onClick={onRefresh}
        disabled={loading}
        style={{
          fontSize: 12, padding: "4px 12px", borderRadius: 5,
          border: "1.5px solid #e2e8f0", background: loading ? "#f1f5f9" : "#fff",
          color: loading ? "#94a3b8" : "#2563eb", cursor: loading ? "not-allowed" : "pointer", fontWeight: 600,
        }}
      >
        {loading ? "Loading..." : "Refresh data"}
      </button>
    </div>
  );
}

// ============================================================
// JOB HUNTING SECTION
// ============================================================

function JobHuntingSection({ data, loading, onRefresh }) {
  if (loading) {
    return <div style={{ padding: 32, textAlign: "center", color: "#64748b", fontSize: 14 }}>Loading jobs data...</div>;
  }

  const jobs = data?.jobs || [];
  const summary = data?.summary || {};
  const tracker = data?.job_tracker || [];
  const bestMatches = summary.best_matches || jobs.slice(0, 5);

  const isEmpty = jobs.length === 0 && !summary.generated_at;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>Job Hunting</h2>
          <p style={{ color: "#64748b", fontSize: 13, marginTop: 4, marginBottom: 0 }}>
            AI/ML and software engineering roles in Ireland
          </p>
        </div>
        <DataRefreshBar loading={loading} onRefresh={onRefresh} />
      </div>

      {/* Daily Summary */}
      <PanelCard title="Daily Summary" count={summary.total_found ? `${summary.total_found} jobs` : undefined}>
        {isEmpty || !summary.generated_at ? (
          <EmptyState
            message="No job data yet. Run the job hunt agent to generate results."
            command="python run_job_hunt.py"
          />
        ) : (
          <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
            <StatBox label="Jobs found" value={summary.total_found || 0} />
            <StatBox label="Avg fit score" value={`${summary.avg_fit_score || 0}/10`} />
            <StatBox label="Applied" value={tracker.length} />
            <StatBox label="Last run" value={summary.generated_at ? new Date(summary.generated_at).toLocaleDateString() : "—"} />
          </div>
        )}
      </PanelCard>

      {/* Best Matches */}
      <PanelCard title="Best Matches" count={bestMatches.length || undefined}>
        {bestMatches.length === 0 ? (
          <EmptyState message="No matches yet." command="python run_job_hunt.py" />
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {bestMatches.map((job, i) => (
              <div key={i} style={{ border: "1px solid #e2e8f0", borderRadius: 7, padding: "12px 14px" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <FitBadge score={job.fit_score} />
                    <span style={{ fontWeight: 600, fontSize: 14 }}>{job.title}</span>
                  </div>
                  {job.url && (
                    <a href={job.url} target="_blank" rel="noreferrer" style={{ fontSize: 12, color: "#2563eb", textDecoration: "none", fontWeight: 600 }}>
                      View job
                    </a>
                  )}
                </div>
                <div style={{ fontSize: 13, color: "#374151", marginBottom: 4 }}>
                  {job.company} — {job.location} {job.type && <span style={{ color: "#64748b" }}>· {job.type}</span>}
                </div>
                {job.fit_reason && (
                  <div style={{ fontSize: 12, color: "#64748b", marginBottom: 4 }}>{job.fit_reason}</div>
                )}
                {job.apply_angle && (
                  <div style={{ fontSize: 12, background: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: 5, padding: "6px 10px", color: "#15803d" }}>
                    Apply angle: {job.apply_angle}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </PanelCard>

      {/* Latest Jobs */}
      <PanelCard title="Latest Jobs" count={jobs.length || undefined}>
        {jobs.length === 0 ? (
          <EmptyState message="No jobs yet." command="python run_job_hunt.py" />
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
              <thead>
                <tr style={{ background: "#f8fafc" }}>
                  {["Fit", "Title", "Company", "Location", "Type", "Link"].map(h => (
                    <th key={h} style={{ padding: "6px 8px", textAlign: "left", fontWeight: 700, color: "#374151", borderBottom: "1.5px solid #e2e8f0", whiteSpace: "nowrap" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {jobs.map((job, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #f1f5f9" }}>
                    <td style={{ padding: "7px 8px" }}><FitBadge score={job.fit_score} /></td>
                    <td style={{ padding: "7px 8px", fontWeight: 600, color: "#1a1a1a" }}>{job.title}</td>
                    <td style={{ padding: "7px 8px", color: "#374151" }}>{job.company}</td>
                    <td style={{ padding: "7px 8px", color: "#64748b" }}>{job.location}</td>
                    <td style={{ padding: "7px 8px", color: "#64748b" }}>{job.type}</td>
                    <td style={{ padding: "7px 8px" }}>
                      {job.url ? (
                        <a href={job.url} target="_blank" rel="noreferrer" style={{ color: "#2563eb", textDecoration: "none", fontWeight: 600 }}>Open</a>
                      ) : <span style={{ color: "#94a3b8" }}>—</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </PanelCard>

      {/* Applied Tracker */}
      <PanelCard title="Applied Tracker" count={tracker.length || undefined}>
        {tracker.length === 0 ? (
          <EmptyState
            message="No applications tracked yet."
            command="from app.agents.job_hunter import mark_applied"
          />
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
              <thead>
                <tr style={{ background: "#f8fafc" }}>
                  {["Date", "Title", "Company", "Status", "Notes"].map(h => (
                    <th key={h} style={{ padding: "6px 8px", textAlign: "left", fontWeight: 700, color: "#374151", borderBottom: "1.5px solid #e2e8f0" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tracker.map((row, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #f1f5f9" }}>
                    <td style={{ padding: "7px 8px", color: "#64748b", whiteSpace: "nowrap" }}>{row.date}</td>
                    <td style={{ padding: "7px 8px", fontWeight: 600 }}>{row.title}</td>
                    <td style={{ padding: "7px 8px" }}>{row.company}</td>
                    <td style={{ padding: "7px 8px" }}>
                      <span style={{ background: "#dcfce7", color: "#15803d", fontSize: 11, fontWeight: 700, padding: "2px 8px", borderRadius: 99, textTransform: "uppercase" }}>
                        {row.status}
                      </span>
                    </td>
                    <td style={{ padding: "7px 8px", color: "#64748b" }}>{row.notes || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </PanelCard>
    </div>
  );
}

// ============================================================
// JOB TRACKER SECTION
// ============================================================

const STATUS_COLORS = {
  saved:      { bg: "#f1f5f9", text: "#475569" },
  applied:    { bg: "#dbeafe", text: "#1d4ed8" },
  interview:  { bg: "#fef9c3", text: "#a16207" },
  rejected:   { bg: "#fee2e2", text: "#b91c1c" },
  offer:      { bg: "#dcfce7", text: "#15803d" },
  closed:     { bg: "#f1f5f9", text: "#94a3b8" },
};

function StatusBadge({ status }) {
  const c = STATUS_COLORS[status] || STATUS_COLORS.saved;
  return (
    <span style={{ background: c.bg, color: c.text, fontSize: 11, fontWeight: 700, padding: "2px 8px", borderRadius: 99, textTransform: "uppercase", whiteSpace: "nowrap" }}>
      {status || "saved"}
    </span>
  );
}

function TrackerTable({ rows, emptyMsg }) {
  if (!rows || rows.length === 0) {
    return <EmptyState message={emptyMsg} command="python run_job_tracker.py import-jobs" />;
  }
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
        <thead>
          <tr style={{ background: "#f8fafc" }}>
            {["SL", "Status", "Fit", "CV Match", "Title", "Company", "Applied", "Link"].map(h => (
              <th key={h} style={{ padding: "6px 8px", textAlign: "left", fontWeight: 700, color: "#374151", borderBottom: "1.5px solid #e2e8f0", whiteSpace: "nowrap" }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((e, i) => (
            <tr key={i} style={{ borderBottom: "1px solid #f1f5f9" }}>
              <td style={{ padding: "7px 8px", textAlign: "center" }}>{e.shortlisted ? "★" : ""}</td>
              <td style={{ padding: "7px 8px" }}><StatusBadge status={e.status} /></td>
              <td style={{ padding: "7px 8px" }}><FitBadge score={e.fit_score} /></td>
              <td style={{ padding: "7px 8px" }}><FitBadge score={e.cv_match_score} /></td>
              <td style={{ padding: "7px 8px", fontWeight: 600, color: "#1a1a1a", maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{e.title}</td>
              <td style={{ padding: "7px 8px", color: "#374151" }}>{e.company}</td>
              <td style={{ padding: "7px 8px", color: "#64748b", whiteSpace: "nowrap" }}>{e.date_applied || "—"}</td>
              <td style={{ padding: "7px 8px" }}>
                {e.job_url
                  ? <a href={e.job_url} target="_blank" rel="noreferrer" style={{ color: "#2563eb", textDecoration: "none", fontWeight: 600 }}>Open</a>
                  : <span style={{ color: "#94a3b8" }}>—</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function JobTrackerSection({ data, loading, onRefresh }) {
  const [trackerTab, setTrackerTab] = useState("all");

  if (loading) {
    return <div style={{ padding: 32, textAlign: "center", color: "#64748b", fontSize: 14 }}>Loading tracker...</div>;
  }

  const all         = data?.all || [];
  const shortlisted = data?.shortlisted || [];
  const applied     = data?.applied || [];

  const views = { all, shortlisted, applied };
  const activeRows = views[trackerTab] || [];

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>Application Tracker</h2>
          <p style={{ color: "#64748b", fontSize: 13, marginTop: 4, marginBottom: 0 }}>
            Tracked jobs with status, fit score, and CV match score
          </p>
        </div>
        <DataRefreshBar loading={loading} onRefresh={onRefresh} />
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        <div style={{ display: "flex", gap: 16, flexWrap: "wrap", flex: 1 }}>
          <StatBox label="Tracked" value={all.length} />
          <StatBox label="Shortlisted" value={shortlisted.length} />
          <StatBox label="Applied / Active" value={applied.length} />
        </div>
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        {[["all", "All"], ["shortlisted", "Shortlisted ★"], ["applied", "Applied / Active"]].map(([key, label]) => (
          <button key={key} onClick={() => setTrackerTab(key)} style={subTabStyle(trackerTab === key)}>
            {label} {views[key].length > 0 && `(${views[key].length})`}
          </button>
        ))}
      </div>

      <PanelCard title={trackerTab === "all" ? "All Tracked Jobs" : trackerTab === "shortlisted" ? "Shortlisted Jobs" : "Applied / Active Jobs"} count={activeRows.length || undefined}>
        <TrackerTable
          rows={activeRows}
          emptyMsg={
            trackerTab === "all"
              ? "No tracked jobs yet. Run: python run_job_tracker.py import-jobs"
              : trackerTab === "shortlisted"
              ? "No shortlisted jobs. Use: python run_job_tracker.py shortlist <url>"
              : "No active applications. Use: python run_job_tracker.py apply <url>"
          }
        />
      </PanelCard>

      <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 8 }}>
        <strong>CLI helpers:</strong>{" "}
        <code style={{ background: "#f1f5f9", padding: "1px 6px", borderRadius: 3 }}>python run_job_tracker.py import-jobs</code>{" · "}
        <code style={{ background: "#f1f5f9", padding: "1px 6px", borderRadius: 3 }}>python run_job_tracker.py shortlist &lt;url&gt;</code>{" · "}
        <code style={{ background: "#f1f5f9", padding: "1px 6px", borderRadius: 3 }}>python run_job_tracker.py apply &lt;url&gt;</code>
      </div>
    </div>
  );
}

function StatBox({ label, value }) {
  return (
    <div style={{ background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: 7, padding: "12px 18px", minWidth: 100, textAlign: "center" }}>
      <div style={{ fontSize: 20, fontWeight: 700, color: "#1e40af" }}>{value}</div>
      <div style={{ fontSize: 11, color: "#64748b", marginTop: 2 }}>{label}</div>
    </div>
  );
}

// ============================================================
// RENTPULSE RESEARCH SECTION
// ============================================================

function RentPulseResearchSection({ data, loading, onRefresh }) {
  if (loading) {
    return <div style={{ padding: 32, textAlign: "center", color: "#64748b", fontSize: 14 }}>Loading research data...</div>;
  }

  const leads = data?.leads || [];
  const complaints = data?.complaints || [];
  const competitors = data?.competitors || [];
  const contentIdeas = data?.content_ideas || [];
  const urgentLeads = leads.filter(l => (l.urgency || "").toLowerCase() === "high");
  const hasAnyData = leads.length > 0 || complaints.length > 0 || competitors.length > 0 || contentIdeas.length > 0;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>Research Results</h2>
          <p style={{ color: "#64748b", fontSize: 13, marginTop: 4, marginBottom: 0 }}>
            Leads, complaints, competitors, and content ideas
          </p>
        </div>
        <DataRefreshBar loading={loading} onRefresh={onRefresh} />
      </div>

      {!hasAnyData && (
        <div style={{ background: "#fffbeb", border: "1.5px solid #fde68a", borderRadius: 8, padding: "14px 16px", marginBottom: 20, fontSize: 13, color: "#92400e" }}>
          No research data yet. Run the research agent to populate these panels.
          <code style={{ display: "block", marginTop: 6, background: "#fef3c7", padding: "4px 8px", borderRadius: 4, fontSize: 12 }}>
            python run_rentpulse_research.py
          </code>
        </div>
      )}

      {/* Urgent Renters */}
      <PanelCard title="Urgent Renters" count={urgentLeads.length || undefined}>
        {urgentLeads.length === 0 ? (
          <EmptyState message="No high-urgency leads yet." command="python run_rentpulse_research.py leads" />
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {urgentLeads.map((lead, i) => (
              <LeadCard key={i} lead={lead} />
            ))}
          </div>
        )}
      </PanelCard>

      {/* Rental Leads */}
      <PanelCard title="Rental Leads" count={leads.length || undefined}>
        {leads.length === 0 ? (
          <EmptyState message="No leads yet." command="python run_rentpulse_research.py leads" />
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {leads.map((lead, i) => (
              <LeadCard key={i} lead={lead} />
            ))}
          </div>
        )}
      </PanelCard>

      {/* Complaints / Pain Points */}
      <PanelCard title="Complaints / Pain Points" count={complaints.length || undefined}>
        {complaints.length === 0 ? (
          <EmptyState message="No complaints data yet." command="python run_rentpulse_research.py complaints" />
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {complaints.map((c, i) => (
              <div key={i} style={{ border: "1px solid #e2e8f0", borderRadius: 7, padding: "11px 14px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                  <span style={{ fontSize: 11, background: "#f1f5f9", color: "#475569", padding: "2px 8px", borderRadius: 99, fontWeight: 600 }}>{c.platform}</span>
                  <span style={{ fontSize: 12, fontWeight: 700, color: "#1a1a1a" }}>{c.theme}</span>
                  {c.frequency && <span style={{ fontSize: 11, color: "#64748b" }}>{c.frequency}</span>}
                </div>
                <div style={{ fontSize: 13, color: "#374151", marginBottom: 6 }}>{c.complaint}</div>
                {c.content_opportunity && (
                  <div style={{ fontSize: 12, color: "#0369a1", background: "#e0f2fe", borderRadius: 5, padding: "4px 8px" }}>
                    Content angle: {c.content_opportunity}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </PanelCard>

      {/* Competitors */}
      <PanelCard title="Competitors" count={competitors.length || undefined}>
        {competitors.length === 0 ? (
          <EmptyState message="No competitor data yet." command="python run_rentpulse_research.py competitors" />
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {competitors.map((comp, i) => (
              <div key={i} style={{ border: "1px solid #e2e8f0", borderRadius: 7, padding: "11px 14px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                  <span style={{ fontWeight: 700, fontSize: 14 }}>{comp.name}</span>
                  <span style={{ fontSize: 11, background: "#f1f5f9", color: "#475569", padding: "2px 8px", borderRadius: 99 }}>{comp.type}</span>
                </div>
                <div style={{ fontSize: 13, color: "#374151", marginBottom: 6 }}>{comp.what_it_does}</div>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  {comp.strengths && (
                    <div style={{ fontSize: 12, color: "#15803d", background: "#dcfce7", borderRadius: 5, padding: "4px 8px" }}>
                      Strengths: {comp.strengths}
                    </div>
                  )}
                  {comp.weaknesses && (
                    <div style={{ fontSize: 12, color: "#b91c1c", background: "#fee2e2", borderRadius: 5, padding: "4px 8px" }}>
                      Gaps: {comp.weaknesses}
                    </div>
                  )}
                </div>
                {comp.rentpulse_advantage && (
                  <div style={{ fontSize: 12, color: "#0369a1", background: "#e0f2fe", borderRadius: 5, padding: "4px 8px", marginTop: 6 }}>
                    RentPulse advantage: {comp.rentpulse_advantage}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </PanelCard>

      {/* Content Ideas */}
      <PanelCard title="Content Ideas" count={contentIdeas.length || undefined}>
        {contentIdeas.length === 0 ? (
          <EmptyState message="No content ideas yet." command="python run_rentpulse_research.py content_ideas" />
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {contentIdeas.map((idea, i) => (
              <div key={i} style={{ border: "1px solid #e2e8f0", borderRadius: 7, padding: "11px 14px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6, flexWrap: "wrap" }}>
                  <span style={{ fontSize: 11, background: "#eff6ff", color: "#1d4ed8", padding: "2px 8px", borderRadius: 99, fontWeight: 600 }}>{idea.platform}</span>
                  {idea.estimated_engagement && (
                    <UrgencyBadge urgency={idea.estimated_engagement === "high" ? "high" : idea.estimated_engagement === "medium" ? "medium" : "low"} />
                  )}
                </div>
                <div style={{ fontSize: 13, fontWeight: 600, color: "#1a1a1a", marginBottom: 4 }}>{idea.idea}</div>
                {idea.hook && (
                  <div style={{ fontSize: 12, color: "#475569", fontStyle: "italic", marginBottom: 4 }}>"{idea.hook}"</div>
                )}
                {idea.why_now && (
                  <div style={{ fontSize: 12, color: "#64748b" }}>Why now: {idea.why_now}</div>
                )}
              </div>
            ))}
          </div>
        )}
      </PanelCard>
    </div>
  );
}

function LeadCard({ lead }) {
  return (
    <div style={{ border: "1px solid #e2e8f0", borderRadius: 7, padding: "11px 14px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
        <UrgencyBadge urgency={lead.urgency} />
        <span style={{ fontSize: 11, background: "#f1f5f9", color: "#475569", padding: "2px 8px", borderRadius: 99, fontWeight: 600 }}>{lead.source}</span>
        {lead.location && <span style={{ fontSize: 12, color: "#374151" }}>{lead.location}</span>}
      </div>
      <div style={{ fontSize: 13, color: "#1a1a1a", marginBottom: 6 }}>{lead.signal}</div>
      {lead.angle && (
        <div style={{ fontSize: 12, color: "#0369a1", background: "#e0f2fe", borderRadius: 5, padding: "4px 8px" }}>
          {lead.angle}
        </div>
      )}
    </div>
  );
}

// ============================================================
// SOCIAL MEDIA PROMOTIONS SECTION  (original content — unchanged)
// ============================================================

function SocialMediaSection({ today, todayName, todayPlatforms, posts, done, copied, news, newsChecked, newsDismissed, agentStatus, onRunAgent, onRegenerate, onMarkDone, onCopyPost, onCopyAndOpen, onDismissNews }) {
  const doneCount = Object.keys(done).length;
  const totalToday = todayPlatforms.length;
  const urgencyColor = { high: "#dc2626", medium: "#d97706", low: "#2563eb" };

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
        <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>Social Media Promotions</h2>
        <button
          onClick={onRunAgent}
          disabled={agentStatus === "running"}
          style={{
            padding: "5px 14px", borderRadius: 6, border: "1.5px solid #2563eb",
            background: agentStatus === "running" ? "#e2e8f0" : "#fff",
            color: agentStatus === "running" ? "#94a3b8" : "#2563eb",
            fontSize: 12, fontWeight: 600,
            cursor: agentStatus === "running" ? "not-allowed" : "pointer",
          }}
        >
          {agentStatus === "running" ? "Generating..." : "Regenerate all"}
        </button>
      </div>

      <p style={{ color: "#555", fontSize: 14, marginTop: 4, marginBottom: 16 }}>
        {todayName} - {doneCount}/{totalToday} posted today
      </p>

      {!newsDismissed && newsChecked && news && (
        <div style={{ background: "#fffbeb", border: `1.5px solid ${urgencyColor[news.urgency] || "#d97706"}`, borderRadius: 8, padding: "14px 16px", marginBottom: 20 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <div style={{ flex: 1 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                <span style={{ fontSize: 11, fontWeight: 700, padding: "2px 8px", borderRadius: 99, background: urgencyColor[news.urgency], color: "#fff", textTransform: "uppercase" }}>
                  {news.urgency} priority
                </span>
                <span style={{ fontSize: 13, fontWeight: 700 }}>News today</span>
              </div>
              <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>{news.headline}</div>
              <div style={{ fontSize: 13, color: "#555" }}>{news.summary}</div>
            </div>
            <button onClick={onDismissNews} style={{ background: "none", border: "none", cursor: "pointer", color: "#94a3b8", fontSize: 18, padding: "0 0 0 12px" }}>x</button>
          </div>
        </div>
      )}

      {!newsChecked && (
        <div style={{ background: "#f1f5f9", border: "1.5px solid #e2e8f0", borderRadius: 8, padding: "12px 16px", marginBottom: 20, fontSize: 13, color: "#64748b" }}>
          Checking for Irish rental news...
        </div>
      )}

      {newsChecked && !news && !newsDismissed && (
        <div style={{ background: "#f1f5f9", border: "1.5px solid #e2e8f0", borderRadius: 8, padding: "12px 16px", marginBottom: 20, fontSize: 13, color: "#64748b" }}>
          No relevant Irish rental news found today.
        </div>
      )}

      <div style={{ background: "#e2e8f0", borderRadius: 99, height: 6, marginBottom: 24 }}>
        <div style={{ background: "#16a34a", borderRadius: 99, height: 6, width: `${totalToday ? (doneCount / totalToday) * 100 : 0}%`, transition: "width 0.3s" }} />
      </div>

      <h3 style={{ fontSize: 14, fontWeight: 700, color: "#374151", marginBottom: 12 }}>Post today</h3>

      <div style={{ display: "flex", flexDirection: "column", gap: 14, marginBottom: 32 }}>
        {todayPlatforms.map((p) => {
          const post = posts[p.platform];
          const typeStyles = getPostTypeColors(post?.postType);
          return (
            <div key={p.platform} style={{ borderRadius: 8, border: `1.5px solid ${done[p.platform] ? "#bbf7d0" : "#e2e8f0"}`, background: done[p.platform] ? "#f0fdf4" : "#fff", padding: 16 }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                  <div style={{ width: 9, height: 9, borderRadius: "50%", background: p.color }} />
                  <span style={{ fontWeight: 600, fontSize: 14, color: done[p.platform] ? "#16a34a" : "#1a1a1a" }}>
                    {p.platform}{done[p.platform] ? " - posted" : ""}
                  </span>
                  <span style={{ fontSize: 12, color: "#64748b" }}>{p.handle}</span>
                </div>
                <a href={p.url} target="_blank" rel="noreferrer" style={{ fontSize: 12, color: "#2563eb", textDecoration: "none", fontWeight: 600 }}>Open platform</a>
              </div>

              {!post && <div style={{ fontSize: 13, color: "#94a3b8" }}>Waiting...</div>}
              {post?.status === "loading" && (
                <div style={{ fontSize: 13, color: "#64748b" }}>
                  {post.retrying ? "Rate limited — retrying in 30s..." : "Generating post..."}
                </div>
              )}
              {post?.status === "error" && (
                <div style={{ fontSize: 13, color: "#dc2626" }}>
                  Failed. <button onClick={() => onRegenerate(p)} style={{ background: "none", border: "none", color: "#2563eb", cursor: "pointer", fontSize: 13, padding: 0 }}>Retry</button>
                </div>
              )}

              {post?.status === "done" && (
                <>
                  <div style={{ display: "inline-flex", alignItems: "center", gap: 8, fontSize: 12, fontWeight: 600, color: typeStyles.text, background: typeStyles.bg, border: `1px solid ${typeStyles.border}`, borderRadius: 999, padding: "5px 10px", marginBottom: 10 }}>
                    <span>{getPostTypeLabel(post.postType)}</span>
                    {post.useDemoVideo && <span>Use RentPulse demo video</span>}
                  </div>

                  {post.note && <div style={{ fontSize: 12, color: "#64748b", marginBottom: 8 }}>{post.note}</div>}

                  <div style={{ background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: 6, padding: "10px 12px", fontSize: 13, whiteSpace: "pre-wrap", lineHeight: 1.65, marginBottom: 10 }}>
                    {post.content}
                  </div>

                  {post.postType === "video" && (
                    <div style={{ background: "#ecfeff", border: "1px solid #a5f3fc", borderRadius: 6, padding: "10px 12px", fontSize: 12, color: "#0f766e", marginBottom: 10 }}>
                      Attach your RentPulse demo video to this one.
                    </div>
                  )}
                  {post.postType === "screenshot" && (
                    <div style={{ background: "#eff6ff", border: "1px solid #bfdbfe", borderRadius: 6, padding: "10px 12px", fontSize: 12, color: "#1d4ed8", marginBottom: 10 }}>
                      Pair this post with a screenshot of the extension or dashboard.
                    </div>
                  )}
                  {post.postType === "text" && (
                    <div style={{ background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: 6, padding: "10px 12px", fontSize: 12, color: "#475569", marginBottom: 10 }}>
                      Post this as text only.
                    </div>
                  )}

                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    <button onClick={() => onCopyPost(p.platform, post.content)} style={{ padding: "6px 14px", borderRadius: 6, border: "1.5px solid #2563eb", background: copied === p.platform ? "#2563eb" : "#fff", color: copied === p.platform ? "#fff" : "#2563eb", fontSize: 12, fontWeight: 600, cursor: "pointer" }}>
                      {copied === p.platform ? "Copied" : "Copy"}
                    </button>
                    <button onClick={() => onCopyAndOpen(p.platform, post.content, p.url)} style={{ padding: "6px 14px", borderRadius: 6, border: "1.5px solid #0f766e", background: "#fff", color: "#0f766e", fontSize: 12, fontWeight: 600, cursor: "pointer" }}>
                      Copy + open
                    </button>
                    <button onClick={() => onMarkDone(p.platform)} disabled={done[p.platform]} style={{ padding: "6px 14px", borderRadius: 6, border: "none", background: done[p.platform] ? "#e2e8f0" : "#16a34a", color: done[p.platform] ? "#94a3b8" : "#fff", fontSize: 12, fontWeight: 600, cursor: done[p.platform] ? "default" : "pointer" }}>
                      {done[p.platform] ? "Posted" : "Mark posted"}
                    </button>
                    <button onClick={() => onRegenerate(p)} style={{ padding: "6px 14px", borderRadius: 6, border: "1.5px solid #ccc", background: "#fff", color: "#333", fontSize: 12, cursor: "pointer" }}>
                      Regenerate
                    </button>
                  </div>
                </>
              )}
            </div>
          );
        })}
      </div>

      <h3 style={{ fontSize: 14, fontWeight: 700, color: "#374151", marginBottom: 12 }}>Week schedule</h3>
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
          <thead>
            <tr>
              {DAY_NAMES.map((d, i) => (
                <th key={d} style={{ padding: "6px 4px", textAlign: "center", fontWeight: 700, color: i === today ? "#2563eb" : "#374151", borderBottom: "2px solid #e2e8f0", background: i === today ? "#eff6ff" : "transparent" }}>
                  {d}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr>
              {DAY_NAMES.map((_, i) => (
                <td key={i} style={{ padding: "8px 4px", verticalAlign: "top", background: i === today ? "#eff6ff" : "transparent" }}>
                  {SCHEDULE.filter((p) => p.days.includes(i)).map((p) => (
                    <div key={p.platform} style={{ display: "flex", alignItems: "center", gap: 3, marginBottom: 3 }}>
                      <div style={{ width: 6, height: 6, borderRadius: "50%", background: p.color, flexShrink: 0 }} />
                      <span style={{ fontSize: 11, color: "#374151" }}>{p.platform}</span>
                    </div>
                  ))}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </>
  );
}

// ============================================================
// RUN CONTROLS SECTION
// ============================================================

const RUN_PROJECTS = [
  {
    key: "rentpulse",
    label: "RentPulse Research",
    description: "Finds leads, complaints, competitors, and content ideas",
    endpoint: "/rentpulse",
  },
  {
    key: "job-hunt",
    label: "Job Hunt",
    description: "Searches for AI/ML and software roles in Ireland",
    endpoint: "/job-hunt",
  },
  {
    key: "support",
    label: "Support Triage",
    description: "Fetches Gmail messages and classifies support tickets",
    endpoint: "/support",
  },
];

function RunStatusBadge({ status }) {
  const map = {
    running:   { bg: "#fef9c3", text: "#a16207", label: "Running…" },
    success:   { bg: "#dcfce7", text: "#15803d", label: "Success" },
    failed:    { bg: "#fee2e2", text: "#b91c1c", label: "Failed" },
  };
  const c = map[status] || { bg: "#f1f5f9", text: "#64748b", label: "Never run" };
  return (
    <span style={{ background: c.bg, color: c.text, fontSize: 11, fontWeight: 700, padding: "2px 8px", borderRadius: 99, textTransform: "uppercase" }}>
      {c.label}
    </span>
  );
}

function RunControlsSection({ runsData, loading, running, onRun, onRunAll, onRefresh }) {
  const anyRunning = Object.values(running).some(Boolean);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>Run Controls</h2>
          <p style={{ color: "#64748b", fontSize: 13, marginTop: 4, marginBottom: 0 }}>
            Trigger agents manually. Runs only when you click — no automation.
          </p>
        </div>
        <DataRefreshBar loading={loading} onRefresh={onRefresh} />
      </div>

      {/* Run All */}
      <div style={{ border: "1.5px solid #e2e8f0", borderRadius: 8, padding: "14px 16px", marginBottom: 20, background: "#f8fafc" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 2 }}>Run All Agents</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>Runs RentPulse → Job Hunt → Support in sequence</div>
          </div>
          <button
            onClick={onRunAll}
            disabled={anyRunning}
            style={{
              padding: "7px 18px", borderRadius: 6, fontWeight: 700, fontSize: 13,
              border: "none",
              background: anyRunning ? "#e2e8f0" : "#1e40af",
              color: anyRunning ? "#94a3b8" : "#fff",
              cursor: anyRunning ? "not-allowed" : "pointer",
            }}
          >
            {anyRunning ? "Running…" : "Run All"}
          </button>
        </div>
      </div>

      {/* Individual project cards */}
      {RUN_PROJECTS.map(({ key, label, description }) => {
        const run = runsData?.[key];
        const isRunning = running[key];
        return (
          <PanelCard key={key} title={label}>
            <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12 }}>
              <p style={{ margin: 0, fontSize: 13, color: "#64748b" }}>{description}</p>
              <button
                onClick={() => onRun(key)}
                disabled={anyRunning}
                style={{
                  flexShrink: 0, padding: "6px 16px", borderRadius: 6, fontWeight: 700, fontSize: 12,
                  border: "1.5px solid #2563eb",
                  background: anyRunning ? "#f1f5f9" : "#fff",
                  color: anyRunning ? "#94a3b8" : "#2563eb",
                  cursor: anyRunning ? "not-allowed" : "pointer",
                }}
              >
                {isRunning ? "Running…" : "Run"}
              </button>
            </div>

            {run && (
              <div style={{ marginTop: 12, paddingTop: 12, borderTop: "1px solid #f1f5f9" }}>
                <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap", marginBottom: 6 }}>
                  <RunStatusBadge status={run.status} />
                  {run.started_at && (
                    <span style={{ fontSize: 11, color: "#64748b" }}>
                      Started {new Date(run.started_at).toLocaleTimeString()}
                    </span>
                  )}
                  {run.finished_at && (
                    <span style={{ fontSize: 11, color: "#64748b" }}>
                      · Finished {new Date(run.finished_at).toLocaleTimeString()}
                    </span>
                  )}
                </div>
                {run.message && (
                  <pre style={{
                    margin: 0, background: run.status === "failed" ? "#fff5f5" : "#f8fafc",
                    border: `1px solid ${run.status === "failed" ? "#fecaca" : "#e2e8f0"}`,
                    borderRadius: 5, padding: "8px 10px", fontSize: 11,
                    color: run.status === "failed" ? "#b91c1c" : "#374151",
                    whiteSpace: "pre-wrap", maxHeight: 90, overflow: "auto",
                  }}>
                    {run.message}
                  </pre>
                )}
              </div>
            )}

            {!run && (
              <div style={{ marginTop: 10, fontSize: 12, color: "#94a3b8" }}>Not run yet this session.</div>
            )}
          </PanelCard>
        );
      })}
    </div>
  );
}

// ============================================================
// ROOT APP
// ============================================================

export default function App() {
  const today = new Date().getDay();
  const todayName = FULL_DAY_NAMES[today];
  const todayPlatforms = SCHEDULE.filter((p) => p.days.includes(today));

  // ---- Social media state (unchanged) ----
  const [posts, setPosts] = useState({});
  const [done, setDone] = useState({});
  const [copied, setCopied] = useState("");
  const [news, setNews] = useState(null);
  const [newsChecked, setNewsChecked] = useState(false);
  const [newsDismissed, setNewsDismissed] = useState(false);
  const [agentStatus, setAgentStatus] = useState("idle");

  // ---- Navigation state ----
  const [section, setSection] = useState("rentpulse");   // "rentpulse" | "jobs" | "payments" | "customers" | "support" | "runs" | "users"
  const [rpTab, setRpTab] = useState("social");           // "social" | "research"
  const [jobsTab, setJobsTab] = useState("search");       // "search" | "tracker"

  // ---- Local data state ----
  const [jobsData, setJobsData] = useState(null);
  const [trackerData, setTrackerData] = useState(null);
  const [rentpulseData, setRentpulseData] = useState(null);
  const [paymentsData, setPaymentsData] = useState(null);
  const [customersData, setCustomersData] = useState(null);
  const [supportData, setSupportData] = useState(null);
  const [jobsLoading, setJobsLoading] = useState(false);
  const [trackerLoading, setTrackerLoading] = useState(false);
  const [researchLoading, setResearchLoading] = useState(false);
  const [paymentsLoading, setPaymentsLoading] = useState(false);
  const [customersLoading, setCustomersLoading] = useState(false);
  const [supportLoading, setSupportLoading] = useState(false);
  const [runsData, setRunsData] = useState(null);
  const [runsLoading, setRunsLoading] = useState(false);
  const [running, setRunning] = useState({ rentpulse: false, "job-hunt": false, support: false });

  // ---- Users / premium state ----
  const [usersData, setUsersData] = useState(null);
  const [usersLoading, setUsersLoading] = useState(false);

  // ---- Init: restore posted state + start social agent ----
  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem("rp_done") || "{}");
      const todayKey = new Date().toDateString();
      setDone(saved[todayKey] || {});
    } catch {}
  }, []);

  useEffect(() => {
    runAgent();
  }, []);

  // ---- Load local data when switching sections ----
  useEffect(() => {
    if (section === "jobs" && !jobsData) loadJobsData();
    if (section === "payments" && !paymentsData) loadPaymentsData();
    if (section === "customers" && !customersData) loadCustomersData();
    if (section === "support" && !supportData) loadSupportData();
    if (section === "jobs" && jobsTab === "tracker" && !trackerData) loadTrackerData();
    if (section === "runs" && !runsData) loadRunsData();
    if (section === "users" && !usersData) loadUsersData();
  }, [section]);

  useEffect(() => {
    if (section === "rentpulse" && rpTab === "research" && !rentpulseData) loadRentpulseData();
  }, [section, rpTab]);

  useEffect(() => {
    if (section === "jobs" && jobsTab === "tracker" && !trackerData) loadTrackerData();
  }, [section, jobsTab]);

  // ---- Data loaders ----
  const loadJobsData = async () => {
    setJobsLoading(true);
    try {
      const res = await fetch(`${DATA_API}/jobs`);
      setJobsData(await res.json());
    } catch {
      setJobsData({ jobs: [], summary: {}, job_tracker: [] });
    } finally {
      setJobsLoading(false);
    }
  };

  const loadTrackerData = async () => {
    setTrackerLoading(true);
    try {
      const res = await fetch(`${DATA_API}/jobs/tracker`);
      setTrackerData(await res.json());
    } catch {
      setTrackerData({ all: [], shortlisted: [], applied: [] });
    } finally {
      setTrackerLoading(false);
    }
  };

  const loadRentpulseData = async () => {
    setResearchLoading(true);
    try {
      const res = await fetch(`${DATA_API}/rentpulse`);
      setRentpulseData(await res.json());
    } catch {
      setRentpulseData({ leads: [], complaints: [], competitors: [], content_ideas: [] });
    } finally {
      setResearchLoading(false);
    }
  };

  const loadPaymentsData = async () => {
    setPaymentsLoading(true);
    try {
      const res = await fetch(`${DATA_API}/payments`);
      setPaymentsData(await res.json());
    } catch {
      setPaymentsData({ payments: [] });
    } finally {
      setPaymentsLoading(false);
    }
  };

  const loadCustomersData = async () => {
    setCustomersLoading(true);
    try {
      const res = await fetch(`${DATA_API}/customers`);
      setCustomersData(await res.json());
    } catch {
      setCustomersData({ customers: [] });
    } finally {
      setCustomersLoading(false);
    }
  };

  const loadSupportData = async () => {
    setSupportLoading(true);
    try {
      const res = await fetch(`${DATA_API}/support`);
      setSupportData(await res.json());
    } catch {
      setSupportData({ tickets: [] });
    } finally {
      setSupportLoading(false);
    }
  };

  const loadRunsData = async () => {
    setRunsLoading(true);
    try {
      const res = await fetch(`${DATA_API}/runs`);
      setRunsData(await res.json());
    } catch {
      setRunsData({});
    } finally {
      setRunsLoading(false);
    }
  };

  const loadUsersData = async () => {
    setUsersLoading(true);
    try {
      const res = await fetch(`${DATA_API}/users`);
      setUsersData(await res.json());
    } catch {
      setUsersData({ users: [] });
    } finally {
      setUsersLoading(false);
    }
  };

  const triggerRun = async (project) => {
    setRunning((prev) => ({ ...prev, [project]: true }));
    try {
      await fetch(`${RUN_API}/${project}`, { method: "POST" });
      // Small delay then refresh so the "running" status shows up
      setTimeout(() => loadRunsData(), 800);
    } catch (e) {
      console.error("[run]", project, e.message);
    } finally {
      setRunning((prev) => ({ ...prev, [project]: false }));
    }
  };

  const triggerRunAll = async () => {
    setRunning({ rentpulse: true, "job-hunt": true, support: true });
    try {
      await fetch(`${RUN_API}/all`, { method: "POST" });
      setTimeout(() => loadRunsData(), 800);
    } catch (e) {
      console.error("[run] all", e.message);
    } finally {
      setRunning({ rentpulse: false, "job-hunt": false, support: false });
    }
  };

  // ---- Social media functions (unchanged) ----
  const generatePost = async (platform, context, attempt = 0) => {
    const recentPosts = loadRecentPosts(platform.platform);
    const prompt = buildUserPrompt(platform.platform, context, recentPosts);

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 30000);

    let res;
    try {
      res = await fetch(API, {
        signal: controller.signal,
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-6",
          max_tokens: 600,
          system: SYSTEM_PROMPT(platform.platform),
          messages: [{ role: "user", content: prompt }],
        }),
      });
    } finally {
      clearTimeout(timer);
    }

    const data = await res.json();

    if (data.type === "error" && data.error?.type === "rate_limit_error" && attempt < 3) {
      setPosts((prev) => ({ ...prev, [platform.platform]: { status: "loading", retrying: true } }));
      await new Promise((r) => setTimeout(r, 30000));
      return generatePost(platform, context, attempt + 1);
    }

    if (data.type === "error") {
      throw new Error(data.error?.message || "API error");
    }

    const raw = data.content?.find((b) => b.type === "text")?.text || "";
    const clean = raw.replace(/```json|```/g, "").trim();
    let parsed;
    try {
      parsed = JSON.parse(clean);
    } catch {
      throw new Error("Failed to parse post JSON: " + clean.slice(0, 100));
    }

    const safePost = {
      content: parsed?.content || "",
      note: parsed?.note || "",
      postType: ["text", "screenshot", "video"].includes(parsed?.postType) ? parsed.postType : "text",
      useDemoVideo: Boolean(parsed?.useDemoVideo) || parsed?.postType === "video",
    };

    if (safePost.content) saveRecentPost(platform.platform, safePost.content);
    return safePost;
  };

  const runAgent = async () => {
    setAgentStatus("running");
    const initial = {};
    todayPlatforms.forEach((p) => { initial[p.platform] = { status: "loading" }; });
    setPosts(initial);

    // Fetch news with a 12s timeout — runs in parallel with post generation
    let newsContext = "";
    const newsPromise = (async () => {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 12000);
      try {
        const res = await fetch(API, {
          signal: controller.signal,
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            model: "claude-sonnet-4-6",
            max_tokens: 1000,
            tools: [{ type: "web_search_20250305", name: "web_search" }],
            system: NEWS_SYSTEM,
            messages: [{ role: "user", content: "Search for Irish rental housing news today. Look for: rent price reports, RTB data, government housing policy, daft.ie or myhome.ie market reports, housing crisis coverage in Irish media. Return the JSON object." }],
          }),
        });
        const data = await res.json();
        const raw = (data.content || []).filter((b) => b.type === "text").map((b) => b.text).join("");
        const clean = raw.replace(/```json|```/g, "").replace(/<cite[^>]*>|<\/cite>/g, "").trim();
        const parsed = JSON.parse(clean);
        if (parsed.hasNews) {
          setNews(parsed);
          return `${parsed.headline}. ${parsed.summary}`;
        } else {
          setNews(false);
        }
      } catch {
        setNews(false);
      } finally {
        clearTimeout(timer);
      }
      return "";
    })();

    // Generate posts immediately — don't wait for news
    for (const platform of todayPlatforms) {
      try {
        const draft = await generatePost(platform, newsContext);
        setPosts((prev) => ({ ...prev, [platform.platform]: { ...draft, status: "done" } }));
      } catch (err) {
        console.error(platform.platform, err.message);
        setPosts((prev) => ({ ...prev, [platform.platform]: { status: "error" } }));
      }
      await new Promise((r) => setTimeout(r, 2000));
    }

    // Wait for news to finish (or timeout) and mark checked
    newsContext = await newsPromise;
    setNewsChecked(true);
    setAgentStatus("done");
  };

  const regenerate = async (platform) => {
    setPosts((prev) => ({ ...prev, [platform.platform]: { status: "loading" } }));
    try {
      const draft = await generatePost(platform, "");
      setPosts((prev) => ({ ...prev, [platform.platform]: { ...draft, status: "done" } }));
    } catch {
      setPosts((prev) => ({ ...prev, [platform.platform]: { status: "error" } }));
    }
  };

  const markDone = (platform) => {
    const todayKey = new Date().toDateString();
    const updated = { ...done, [platform]: true };
    setDone(updated);
    try {
      const all = JSON.parse(localStorage.getItem("rp_done") || "{}");
      all[todayKey] = updated;
      localStorage.setItem("rp_done", JSON.stringify(all));
    } catch {}
  };

  const copyPost = (platform, content) => {
    navigator.clipboard.writeText(content);
    setCopied(platform);
    setTimeout(() => setCopied(""), 2000);
  };

  const copyAndOpen = (platform, content, url) => {
    navigator.clipboard.writeText(content);
    window.open(url, "_blank", "noopener,noreferrer");
    setCopied(platform);
    setTimeout(() => setCopied(""), 2000);
  };

  // ============================================================
  // RENDER
  // ============================================================

  return (
    <div style={{ fontFamily: "system-ui, sans-serif", maxWidth: 760, margin: "0 auto", padding: 24 }}>

      {/* Top-level section navigation */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 24, paddingBottom: 16, borderBottom: "2px solid #e2e8f0" }}>
        <button onClick={() => setSection("rentpulse")} style={sectionTabStyle(section === "rentpulse")}>
          RentPulse
        </button>
        <button onClick={() => setSection("jobs")} style={sectionTabStyle(section === "jobs")}>
          Job Hunting
        </button>
        <button onClick={() => setSection("payments")} style={sectionTabStyle(section === "payments")}>
          Payments
        </button>
        <button onClick={() => setSection("customers")} style={sectionTabStyle(section === "customers")}>
          Customers
        </button>
        <button onClick={() => setSection("support")} style={sectionTabStyle(section === "support")}>
          Support
        </button>
        <button onClick={() => setSection("runs")} style={sectionTabStyle(section === "runs")}>
          Run Controls
        </button>
        <button onClick={() => setSection("users")} style={sectionTabStyle(section === "users")}>
          Users
        </button>
      </div>

      {/* ---- RENTPULSE SECTION ---- */}
      {section === "rentpulse" && (
        <>
          {/* Sub-tab navigation */}
          <div style={{ display: "flex", gap: 8, marginBottom: 24 }}>
            <button onClick={() => setRpTab("social")} style={subTabStyle(rpTab === "social")}>
              Social Media Promotions
            </button>
            <button onClick={() => setRpTab("research")} style={subTabStyle(rpTab === "research")}>
              Research Results
            </button>
          </div>

          {rpTab === "social" && (
            <SocialMediaSection
              today={today}
              todayName={todayName}
              todayPlatforms={todayPlatforms}
              posts={posts}
              done={done}
              copied={copied}
              news={news}
              newsChecked={newsChecked}
              newsDismissed={newsDismissed}
              agentStatus={agentStatus}
              onRunAgent={runAgent}
              onRegenerate={regenerate}
              onMarkDone={markDone}
              onCopyPost={copyPost}
              onCopyAndOpen={copyAndOpen}
              onDismissNews={() => setNewsDismissed(true)}
            />
          )}

          {rpTab === "research" && (
            <RentPulseResearchSection
              data={rentpulseData}
              loading={researchLoading}
              onRefresh={() => { setRentpulseData(null); loadRentpulseData(); }}
            />
          )}
        </>
      )}

      {/* ---- JOB HUNTING SECTION ---- */}
      {section === "jobs" && (
        <>
          <div style={{ display: "flex", gap: 8, marginBottom: 24 }}>
            <button onClick={() => setJobsTab("search")} style={subTabStyle(jobsTab === "search")}>
              Job Search
            </button>
            <button onClick={() => setJobsTab("tracker")} style={subTabStyle(jobsTab === "tracker")}>
              Application Tracker
            </button>
          </div>
          {jobsTab === "search" && (
            <JobHuntingSection
              data={jobsData}
              loading={jobsLoading}
              onRefresh={() => { setJobsData(null); loadJobsData(); }}
            />
          )}
          {jobsTab === "tracker" && (
            <JobTrackerSection
              data={trackerData}
              loading={trackerLoading}
              onRefresh={() => { setTrackerData(null); loadTrackerData(); }}
            />
          )}
        </>
      )}

      {/* ---- PAYMENTS SECTION ---- */}
      {section === "payments" && (
        <div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
            <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>Payments</h2>
            <button onClick={() => { setPaymentsData(null); loadPaymentsData(); }} style={{ fontSize: 12, padding: "4px 10px", cursor: "pointer" }}>
              Refresh
            </button>
          </div>
          {paymentsLoading && <p style={{ color: "#64748b" }}>Loading...</p>}
          {!paymentsLoading && paymentsData && (
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ background: "#f8fafc", textAlign: "left" }}>
                  <th style={{ padding: "8px 10px", borderBottom: "1px solid #e2e8f0" }}>Email</th>
                  <th style={{ padding: "8px 10px", borderBottom: "1px solid #e2e8f0" }}>Amount</th>
                  <th style={{ padding: "8px 10px", borderBottom: "1px solid #e2e8f0" }}>Timestamp</th>
                  <th style={{ padding: "8px 10px", borderBottom: "1px solid #e2e8f0" }}>Session ID</th>
                </tr>
              </thead>
              <tbody>
                {paymentsData.payments.length === 0 && (
                  <tr><td colSpan={4} style={{ padding: "12px 10px", color: "#94a3b8" }}>No payments found.</td></tr>
                )}
                {paymentsData.payments.map((p, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #f1f5f9" }}>
                    <td style={{ padding: "7px 10px" }}>{p.email || "—"}</td>
                    <td style={{ padding: "7px 10px" }}>${(p.amount / 100).toFixed(2)}</td>
                    <td style={{ padding: "7px 10px" }}>{p.timestamp ? new Date(p.timestamp).toLocaleString() : "—"}</td>
                    <td style={{ padding: "7px 10px", fontSize: 11, color: "#64748b", wordBreak: "break-all" }}>{p.session_id || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* ---- CUSTOMERS SECTION ---- */}
      {section === "customers" && (
        <div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
            <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>Customers</h2>
            <button onClick={() => { setCustomersData(null); loadCustomersData(); }} style={{ fontSize: 12, padding: "4px 10px", cursor: "pointer" }}>
              Refresh
            </button>
          </div>
          {customersLoading && <p style={{ color: "#64748b" }}>Loading...</p>}
          {!customersLoading && customersData && (
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ background: "#f8fafc", textAlign: "left" }}>
                  <th style={{ padding: "8px 10px", borderBottom: "1px solid #e2e8f0" }}>Email</th>
                  <th style={{ padding: "8px 10px", borderBottom: "1px solid #e2e8f0" }}>Amount</th>
                  <th style={{ padding: "8px 10px", borderBottom: "1px solid #e2e8f0" }}>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {customersData.customers.length === 0 && (
                  <tr><td colSpan={3} style={{ padding: "12px 10px", color: "#94a3b8" }}>No customers found.</td></tr>
                )}
                {customersData.customers.map((c, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #f1f5f9" }}>
                    <td style={{ padding: "7px 10px" }}>{c.email || "—"}</td>
                    <td style={{ padding: "7px 10px" }}>${(c.amount / 100).toFixed(2)}</td>
                    <td style={{ padding: "7px 10px" }}>{c.timestamp ? new Date(c.timestamp).toLocaleString() : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* ---- RUN CONTROLS SECTION ---- */}
      {section === "runs" && (
        <RunControlsSection
          runsData={runsData}
          loading={runsLoading}
          running={running}
          onRun={triggerRun}
          onRunAll={triggerRunAll}
          onRefresh={() => { setRunsData(null); loadRunsData(); }}
        />
      )}

      {/* ---- USERS / PREMIUM SECTION ---- */}
      {section === "users" && (
        <div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
            <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>Users</h2>
            <button onClick={() => { setUsersData(null); loadUsersData(); }} style={{ fontSize: 12, padding: "4px 10px", cursor: "pointer" }}>
              Refresh
            </button>
          </div>

          {/* Premium gating note */}
          <div style={{ marginBottom: 16, padding: "10px 14px", background: "#f0f9ff", border: "1px solid #bae6fd", borderRadius: 6, fontSize: 12, color: "#0369a1" }}>
            <strong>Premium gating is active.</strong> Users with <code>premium_status: true</code> get access to leads research, competitor research, and scam detection. Free users get content ideas and complaints only.
            <br />
            <span style={{ color: "#64748b" }}>To grant premium locally for testing: <code>python -c "from app.agents.user_linker import create_user_if_missing, link_payment_to_user; create_user_if_missing('email'); link_payment_to_user('test_01', 'email')"</code></span>
          </div>

          {usersLoading && <p style={{ color: "#64748b" }}>Loading...</p>}
          {!usersLoading && usersData && (
            <>
              {/* Summary */}
              <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
                <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: "12px 20px", minWidth: 120 }}>
                  <div style={{ fontSize: 11, color: "#64748b", marginBottom: 4 }}>Total Users</div>
                  <div style={{ fontSize: 24, fontWeight: 700 }}>{usersData.users.length}</div>
                </div>
                <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: "12px 20px", minWidth: 120 }}>
                  <div style={{ fontSize: 11, color: "#64748b", marginBottom: 4 }}>Premium</div>
                  <div style={{ fontSize: 24, fontWeight: 700, color: "#15803d" }}>
                    {usersData.users.filter(u => u.premium_status).length}
                  </div>
                </div>
                <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: "12px 20px", minWidth: 120 }}>
                  <div style={{ fontSize: 11, color: "#64748b", marginBottom: 4 }}>Free</div>
                  <div style={{ fontSize: 24, fontWeight: 700, color: "#64748b" }}>
                    {usersData.users.filter(u => !u.premium_status).length}
                  </div>
                </div>
              </div>

              {/* Users table */}
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                <thead>
                  <tr style={{ background: "#f8fafc", textAlign: "left" }}>
                    <th style={{ padding: "8px 10px", borderBottom: "1px solid #e2e8f0" }}>Email</th>
                    <th style={{ padding: "8px 10px", borderBottom: "1px solid #e2e8f0" }}>Status</th>
                    <th style={{ padding: "8px 10px", borderBottom: "1px solid #e2e8f0" }}>Created</th>
                    <th style={{ padding: "8px 10px", borderBottom: "1px solid #e2e8f0" }}>Linked Sessions</th>
                    <th style={{ padding: "8px 10px", borderBottom: "1px solid #e2e8f0" }}></th>
                  </tr>
                </thead>
                <tbody>
                  {usersData.users.length === 0 && (
                    <tr><td colSpan={5} style={{ padding: "12px 10px", color: "#94a3b8" }}>No users found. Users are created automatically on first payment.</td></tr>
                  )}
                  {usersData.users.map((u, i) => (
                    <tr key={i} style={{ borderBottom: "1px solid #f1f5f9" }}>
                      <td style={{ padding: "7px 10px" }}>{u.email || "—"}</td>
                      <td style={{ padding: "7px 10px" }}>
                        {u.premium_status
                          ? <span style={{ background: "#dcfce7", color: "#15803d", fontSize: 11, fontWeight: 700, padding: "2px 8px", borderRadius: 99 }}>Premium</span>
                          : <span style={{ background: "#f1f5f9", color: "#64748b", fontSize: 11, fontWeight: 700, padding: "2px 8px", borderRadius: 99 }}>Free</span>
                        }
                      </td>
                      <td style={{ padding: "7px 10px" }}>{u.created_at ? new Date(u.created_at).toLocaleDateString() : "—"}</td>
                      <td style={{ padding: "7px 10px", fontSize: 11, color: "#64748b" }}>
                        {(u.linked_payment_session_ids || []).length} session{(u.linked_payment_session_ids || []).length !== 1 ? "s" : ""}
                      </td>
                      <td style={{ padding: "7px 10px" }}>
                        {!u.premium_status && (
                          <span
                            title="Upgrade not yet wired — use link_payment_to_user() locally to grant premium"
                            style={{ fontSize: 11, color: "#9ca3af", border: "1px solid #e5e7eb", borderRadius: 4, padding: "2px 8px", cursor: "default" }}
                          >
                            Upgrade
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </div>
      )}

      {/* ---- SUPPORT SECTION ---- */}
      {section === "support" && (
        <div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
            <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>Support Tickets</h2>
            <button onClick={() => { setSupportData(null); loadSupportData(); }} style={{ fontSize: 12, padding: "4px 10px", cursor: "pointer" }}>
              Refresh
            </button>
          </div>
          {supportLoading && <p style={{ color: "#64748b" }}>Loading...</p>}
          {!supportLoading && supportData && (
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ background: "#f8fafc", textAlign: "left" }}>
                  <th style={{ padding: "8px 10px", borderBottom: "1px solid #e2e8f0" }}>Sender</th>
                  <th style={{ padding: "8px 10px", borderBottom: "1px solid #e2e8f0" }}>Category</th>
                  <th style={{ padding: "8px 10px", borderBottom: "1px solid #e2e8f0" }}>Priority</th>
                  <th style={{ padding: "8px 10px", borderBottom: "1px solid #e2e8f0" }}>Sentiment</th>
                  <th style={{ padding: "8px 10px", borderBottom: "1px solid #e2e8f0" }}>Date</th>
                </tr>
              </thead>
              <tbody>
                {supportData.tickets.length === 0 && (
                  <tr><td colSpan={5} style={{ padding: "12px 10px", color: "#94a3b8" }}>No support tickets found.</td></tr>
                )}
                {supportData.tickets.map((t, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #f1f5f9" }}>
                    <td style={{ padding: "7px 10px" }}>{t.sender || "—"}</td>
                    <td style={{ padding: "7px 10px" }}>{t.category || "—"}</td>
                    <td style={{ padding: "7px 10px" }}>{t.priority || "—"}</td>
                    <td style={{ padding: "7px 10px" }}>{t.sentiment || "—"}</td>
                    <td style={{ padding: "7px 10px" }}>{t.date || t.triaged_at || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
