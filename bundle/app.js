import { AnnaAppRuntime } from "/static/anna-apps/_sdk/latest/index.js";
import { TOOLS, METHODS } from "./tools.js";

const APPLIED_KEY = "resumatch:applied";
const SCRAPE_WANTED = 120;
const ENSURE_PASSED = 15;
const MATCH_THRESHOLD = 80;
const SCRAPE_TIMEOUT_MS = 300_000;
const MATCH_TIMEOUT_MS = 120_000;
const PDF_TIMEOUT_MS = 180_000;

const $ = (id) => document.getElementById(id);
let state = { packs: [], match: null, scrape: null, profile: null };

function show(el) { el?.classList.remove("hidden"); }
function hide(el) { el?.classList.add("hidden"); }

function unwrap(out) {
  if (out?.error) throw new Error(out.error.message || "Tool error");
  const payload = out?.result ?? out;
  if (payload?.error) throw new Error(payload.error.message || "Tool error");
  if (payload?.success === false) throw new Error(payload.message || "Tool failed");
  return payload?.data ?? payload;
}

function loadApplied() {
  try {
    const raw = localStorage.getItem(APPLIED_KEY);
    return raw ? new Set(JSON.parse(raw)) : new Set();
  } catch {
    return new Set();
  }
}

function saveApplied(set) {
  localStorage.setItem(APPLIED_KEY, JSON.stringify([...set]));
}

async function invokeTool(anna, toolKey, args, timeoutMs) {
  const out = await anna.tools.invoke(
    { tool_id: TOOLS[toolKey], method: METHODS[toolKey], args, timeoutMs },
    timeoutMs ? { timeoutMs } : undefined,
  );
  if (out?.ok === false) throw new Error(out.error?.message || "RPC failed");
  return unwrap(out);
}

function isProfileComplete(profile) {
  if (!profile?.exists) return false;
  if (profile.profile_complete != null) return Boolean(profile.profile_complete);
  return Boolean(String(profile.search_term || "").trim());
}

function fillOnboardingForm(profile) {
  const form = $("onboard-form");
  if (!form || !profile) return;
  if (profile.name) form.name.value = profile.name;
  form.search_term.value = profile.search_term || "";
  form.target_skills.value = Array.isArray(profile.target_skills)
    ? profile.target_skills.join(", ")
    : "";
  if (profile.domain) form.domain.value = profile.domain;
  if (profile.seniority) form.seniority.value = profile.seniority;
  if (profile.years_experience != null) form.years.value = profile.years_experience;
  if (profile.location) form.location.value = profile.location;
  if (profile.resume_tex) form.latex.value = profile.resume_tex;
}

function setUserChip(name) {
  const chip = $("user-chip");
  if (!name) { hide(chip); return; }
  const initials = name.split(/\s+/).map((w) => w[0]).join("").slice(0, 2).toUpperCase();
  chip.textContent = initials || "?";
  show(chip);
}

function switchView(view) {
  for (const el of document.querySelectorAll(".view")) hide(el);
  show($(`view-${view}`));
  for (const btn of document.querySelectorAll(".nav-item")) {
    btn.classList.toggle("active", btn.dataset.view === view);
  }
  const titles = {
    dashboard: ["Dashboard", "Job automation overview"],
    jobs: ["Job Listings", "Matched roles ready for manual apply"],
    profile: ["Profile", "Search query, skills, and resume"],
  };
  const [title, sub] = titles[view] || titles.dashboard;
  $("page-title").textContent = title;
  $("page-subtitle").textContent = sub;
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function escapeAttr(s) {
  return escapeHtml(s).replace(/'/g, "&#39;");
}

function shortPath(p) {
  if (!p) return "—";
  const parts = String(p).split("/");
  return parts.length > 3 ? "…/" + parts.slice(-3).join("/") : p;
}

function downloadPdfBase64(base64, filename) {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
  const blob = new Blob([bytes], { type: "application/pdf" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename || "resume.pdf";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

async function exportResumePdf(anna, jobIndex, btn) {
  const label = btn.textContent;
  btn.disabled = true;
  btn.textContent = "Building PDF…";
  try {
    const data = await invokeTool(
      anna,
      "composer",
      { action: "compile_pdf", job_index: jobIndex },
      PDF_TIMEOUT_MS,
    );
    downloadPdfBase64(data.pdf_base64, data.pdf_filename);
    btn.textContent = "✓ Downloaded";
    setTimeout(() => {
      btn.textContent = label;
      btn.disabled = false;
    }, 2500);
  } catch (err) {
    btn.textContent = "PDF failed";
    btn.title = err.message || String(err);
    setTimeout(() => {
      btn.textContent = label;
      btn.title = "";
      btn.disabled = false;
    }, 3500);
    throw err;
  }
}

function renderDashboard(packs, appliedSet, scrape, match) {
  const count = packs?.length || 0;
  const applied = [...appliedSet].filter((i) => packs.some((p) => String(p.job_index) === i)).length;
  const scores = packs.map((p) => p.match_score || 0).filter(Boolean);
  const avg = scores.length ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : null;

  $("kpi-matched").textContent = String(count);
  $("kpi-matched-sub").textContent = scrape?.count
    ? `${scrape.count} scraped from Indeed`
    : "Run Sync jobs";
  $("kpi-applied").textContent = String(applied);
  $("kpi-avg-score").textContent = avg != null ? `${avg}%` : "—";
  $("kpi-score-sub").textContent = match?.fallback_used
    ? "Below 80% — review matches"
    : "Target ≥ 80%";
  $("kpi-resumes").textContent = String(count);

  const src = $("source-list");
  const jobCount = scrape?.count ?? 0;
  const status = jobCount > 0 ? "active" : scrape ? "error" : "idle";
  const statusLabel = jobCount > 0 ? "ACTIVE" : scrape?.warning ? "ERROR" : "IDLE";
  const query = scrape?.search_term || state.profile?.search_term || "—";
  const when = scrape?.fetched_at ? "just now" : "not run";
  src.innerHTML = `
    <li>
      <span><strong>Indeed</strong> · ${escapeHtml(query)} · ${jobCount} jobs · ${when}</span>
      <span class="badge ${status}">${statusLabel}</span>
    </li>
    <li>
      <span><strong>Google Jobs</strong> · via JobSpy · bundled with Indeed</span>
      <span class="badge ${jobCount > 0 ? "active" : "idle"}">${jobCount > 0 ? "ACTIVE" : "IDLE"}</span>
    </li>
  `;

  const ready = count;
  const chart = $("pipeline-chart");
  const stages = [
    { label: "Matched", count: ready, color: "#6366f1" },
    { label: "Review", count: Math.max(0, ready - applied), color: "#22c55e" },
    { label: "Applied", count: applied, color: "#f97316" },
  ];
  const max = Math.max(...stages.map((s) => s.count), 1);
  chart.innerHTML = stages
    .map(
      (s) => `
    <div class="pipe-col">
      <div class="pipe-count">${s.count}</div>
      <div class="pipe-bar" style="height:${Math.max(12, (s.count / max) * 120)}px;background:${s.color}"></div>
      <div class="pipe-label">${s.label}</div>
    </div>`,
    )
    .join("");
}

function renderJobs(packs, appliedSet, options = {}) {
  const anna = options.anna;
  const list = $("jobs-list");
  const wrap = $("jobs-wrap");
  const empty = $("empty-state");
  const meta = $("jobs-meta");
  const filter = ($("job-filter")?.value || "").toLowerCase();

  let visible = packs || [];
  if (filter) {
    visible = visible.filter(
      (p) =>
        `${p.job_title} ${p.company}`.toLowerCase().includes(filter),
    );
  }

  if (!visible.length) {
    hide(wrap);
    show(empty);
    meta.textContent = packs?.length ? "No jobs match your filter." : "";
    return;
  }

  hide(empty);
  show(wrap);
  meta.textContent = `${visible.length} job${visible.length === 1 ? "" : "s"}${
    options.fallbackUsed ? " · below 80% — review before applying" : ""
  }`;

  list.innerHTML = "";
  for (const pack of visible) {
    const idx = pack.job_index ?? 0;
    const applied = appliedSet.has(String(idx));
    const card = document.createElement("article");
    card.className = "job-card" + (applied ? " applied" : "");
    card.innerHTML = `
      <div class="job-head">
        <h3>${escapeHtml(pack.job_title || "Untitled")}</h3>
        <span class="score">${Math.round(pack.match_score || 0)}% match</span>
      </div>
      <p class="company">${escapeHtml(pack.company || "")}</p>
      <div class="job-actions">
        <a class="btn small primary" href="${escapeAttr(pack.apply_url || "#")}" target="_blank" rel="noopener">Open & apply</a>
        <button type="button" class="btn small secondary btn-pdf" data-index="${idx}">Resume to PDF</button>
        <button type="button" class="btn small ghost btn-applied" data-index="${idx}">
          ${applied ? "✓ Applied" : "Mark applied"}
        </button>
      </div>
      <p class="resume-path" title="${escapeAttr(pack.resume_tex_path || "")}">Tailored .tex saved locally · click Resume to PDF to download</p>
    `;
    list.appendChild(card);
  }

  list.querySelectorAll(".btn-applied").forEach((btn) => {
    btn.addEventListener("click", () => {
      const idx = String(btn.dataset.index);
      if (appliedSet.has(idx)) appliedSet.delete(idx);
      else appliedSet.add(idx);
      saveApplied(appliedSet);
      renderJobs(packs, appliedSet, options);
      renderDashboard(packs, appliedSet, state.scrape, state.match);
    });
  });

  if (anna) {
    list.querySelectorAll(".btn-pdf").forEach((btn) => {
      btn.addEventListener("click", () => {
        exportResumePdf(anna, Number(btn.dataset.index), btn).catch(() => {});
      });
    });
  }
}

async function getProfile(anna) {
  return invokeTool(anna, "profile", { action: "get" });
}

async function saveProfile(anna, form) {
  const name = form.name.value.trim();
  const latex = form.latex.value.trim();
  const searchTerm = form.search_term.value.trim();
  if (!name || !latex) throw new Error("Name and resume are required.");
  if (!searchTerm) throw new Error("Job search query is required (keep it short).");

  return invokeTool(anna, "profile", {
    action: "save",
    name,
    domain: form.domain.value,
    seniority: form.seniority.value,
    years_experience: Number(form.years.value) || 0,
    location: form.location.value.trim() || "India",
    search_term: searchTerm,
    target_skills: form.target_skills.value.trim(),
    resume_latex: latex,
  });
}

async function runPipeline(anna, onStep) {
  onStep("Loading profile…", false);
  const profile = await getProfile(anna);
  if (!isProfileComplete(profile)) {
    switchView("profile");
    throw new Error("Complete Profile first — set a short Indeed search query.");
  }
  state.profile = profile;

  onStep(`Scraping up to ${SCRAPE_WANTED} jobs (Indeed uses short query from profile)…`, false);
  const scrape = await invokeTool(
    anna,
    "scraper",
    {
      action: "scrape",
      use_profile: true,
      mode: "free",
      results_wanted: SCRAPE_WANTED,
      hours_old: 24,
      persist: true,
      max_response_jobs: 5,
    },
    SCRAPE_TIMEOUT_MS,
  );
  state.scrape = scrape;

  if (!scrape.count || scrape.count === 0) {
    throw new Error(
      scrape.warning ||
        "Indeed returned 0 jobs. Edit Profile — use a short query like \"Python developer\".",
    );
  }

  onStep(`Scored ${scrape.count} jobs. Matching against your resume…`, false);
  const match = await invokeTool(
    anna,
    "matcher",
    { action: "score", threshold: MATCH_THRESHOLD, ensure_passed: ENSURE_PASSED },
    MATCH_TIMEOUT_MS,
  );
  state.match = match;

  if (!match.effective_passed_count && !match.passed_count) {
    throw new Error("No jobs to tailor after matching. Try different search keywords.");
  }

  onStep("Tailoring Skills section…", false);
  await invokeTool(anna, "composer", { action: "compose_all" });

  onStep("Building apply packs…", false);
  await invokeTool(anna, "pack", { action: "prepare_all" });

  const listData = await invokeTool(anna, "pack", { action: "list" });
  listData.fallback_used = match.fallback_used;
  state.packs = listData.packs || [];
  onStep(`Done — ${state.packs.length} jobs ready.`, false);
  return listData;
}

function onStep(msg, isError = false) {
  const el = $("pipeline-status");
  el.textContent = msg;
  el.classList.toggle("error", isError);
}

function showApp(profile) {
  hide($("boot-screen"));
  show($("app"));
  if (profile?.name) setUserChip(profile.name);
  if (!isProfileComplete(profile)) {
    fillOnboardingForm(profile);
    switchView("profile");
  } else {
    switchView("dashboard");
  }
}

async function main() {
  const appliedSet = loadApplied();

  let anna;
  try {
    anna = await AnnaAppRuntime.connect();
    await anna.window.set_title({ title: "ResuMatch" });
  } catch {
    hide($("boot-screen"));
    $("boot-screen").innerHTML = "<p>Run ./scripts/dev.sh from repo root.</p>";
    return;
  }

  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.addEventListener("click", () => switchView(btn.dataset.view));
  });

  $("job-filter")?.addEventListener("input", () => {
    renderJobs(state.packs, appliedSet, { fallbackUsed: state.match?.fallback_used, anna });
  });

  $("onboard-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    hide($("onboard-error"));
    const btn = e.target.querySelector('button[type="submit"]');
    btn.disabled = true;
    try {
      const data = await saveProfile(anna, e.target);
      state.profile = data;
      setUserChip(data.name);
      onStep("Profile saved.");
      switchView("dashboard");
    } catch (err) {
      $("onboard-error").textContent = err.message;
      show($("onboard-error"));
    } finally {
      btn.disabled = false;
    }
  });

  $("btn-refresh").addEventListener("click", async () => {
    const btn = $("btn-refresh");
    btn.disabled = true;
    try {
      const listData = await runPipeline(anna, onStep);
      renderJobs(listData.packs || [], appliedSet, {
        fallbackUsed: listData.fallback_used,
        anna,
      });
      renderDashboard(listData.packs || [], appliedSet, state.scrape, state.match);
      switchView("jobs");
    } catch (err) {
      let msg = err.message || String(err);
      if (/executa process exited/i.test(msg)) {
        msg += " — restart with ./scripts/dev.sh";
      }
      onStep(`Error: ${msg}`, true);
    } finally {
      btn.disabled = false;
    }
  });

  try {
    const profile = await getProfile(anna);
    state.profile = profile;
    showApp(profile);

    if (profile?.exists && isProfileComplete(profile)) {
      const listData = await invokeTool(anna, "pack", { action: "list" });
      state.packs = listData.packs || [];
      if (state.packs.length) {
        renderJobs(state.packs, appliedSet, { anna });
        renderDashboard(state.packs, appliedSet, null, null);
      }
    } else if (profile?.exists) {
      fillOnboardingForm(profile);
    }
  } catch {
    showApp(null);
    switchView("profile");
  }
}

main();
