import { AnnaAppRuntime } from "/static/anna-apps/_sdk/latest/index.js";
import * as pdfjsLib from "./vendor/pdfjs/pdf.min.mjs";
import { TOOLS, METHODS } from "./tools.js";
import {
  applyRoleToForm,
  fillProfileForm,
  isProfileComplete,
  loadJobCatalog,
  populateDomainSelect,
  populateRoleSelect,
  findRole,
} from "./profile.js";

pdfjsLib.GlobalWorkerOptions.workerSrc = new URL("./vendor/pdfjs/pdf.worker.min.mjs", import.meta.url).href;

const STATUS_KEY = "resumatch:status";
const APPLIED_KEY = "resumatch:applied";
const FILTER_PREFS_KEY = "resumatch:scrape-filters";
const LAST_FETCH_KEY = "resumatch:last-fetch";
const SCRAPE_RESULTS_WANTED = 500;
const SCRAPE_TIMEOUT_MS = 300_000;
const COMPOSE_TIMEOUT_MS = 600_000;
const PDF_TIMEOUT_MS = 180_000;

const STATUSES = ["saved", "applied", "interview", "offer", "rejected"];
const STATUS_LABEL = {
  saved: "Saved",
  applied: "Applied",
  interview: "Interview",
  offer: "Offer",
  rejected: "Rejected",
};

const $ = (id) => document.getElementById(id);
let state = {
  packs: [],
  scrape: null,
  profile: null,
  catalog: null,
  profileModalForced: false,
  statusFilter: "all",
  listSeniority: "all",
  listHours: 0,
  cacheStatus: null,
  anna: null,
};

function show(el) { el?.classList.remove("hidden"); }
function hide(el) { el?.classList.add("hidden"); }

function unwrap(out) {
  if (out?.error) throw new Error(out.error.message || "Tool error");
  const payload = out?.result ?? out;
  if (payload?.error) throw new Error(payload.error.message || "Tool error");
  if (payload?.success === false) throw new Error(payload.message || "Tool failed");
  return payload?.data ?? payload;
}

async function invokeTool(anna, toolKey, args, timeoutMs) {
  const out = await anna.tools.invoke(
    { tool_id: TOOLS[toolKey], method: METHODS[toolKey], args, timeoutMs },
    timeoutMs ? { timeoutMs } : undefined,
  );
  if (out?.ok === false) throw new Error(out.error?.message || "RPC failed");
  return unwrap(out);
}

/** Turn raw service/transport errors into calm, user-facing messages. */
function friendlyError(err) {
  const raw = (err && err.message) || String(err || "");
  if (/executa process exited|tool_failed|executa_unavailable|agent_unavailable/i.test(raw)) {
    return "The job service hit a snag and is restarting. Give it a few seconds and try again.";
  }
  if (/tool_timeout|timed out|timeout/i.test(raw)) {
    return "That took longer than expected. Please try again.";
  }
  if (/permission_denied/i.test(raw)) {
    return "This action isn't permitted right now.";
  }
  return raw || "Something went wrong. Please try again.";
}

/** Fetch every apply pack across pages so large job counts never overflow RPC. */
async function fetchAllPacks(anna) {
  const limit = 50;
  let offset = 0;
  let packs = [];
  let total = Infinity;
  while (offset < total) {
    const page = await invokeTool(anna, "pack", { action: "list", offset, limit });
    total = page.total ?? page.count ?? packs.length;
    packs = packs.concat(page.packs || []);
    if (!page.has_more || !(page.packs || []).length) break;
    offset += limit;
  }
  return packs;
}

/* ---------------- storage: status + filters ---------------- */
function jobKey(pack) {
  return String(pack?.apply_url || `${pack?.company || ""}|${pack?.job_title || ""}`);
}

function loadStatusMap() {
  try {
    const raw = localStorage.getItem(STATUS_KEY);
    if (raw) return JSON.parse(raw);
  } catch { /* ignore */ }
  // migrate legacy applied-set (keyed by job_index) -> nothing reliable, start fresh
  return {};
}

function saveStatusMap(map) {
  localStorage.setItem(STATUS_KEY, JSON.stringify(map));
}

function getStatus(map, pack) {
  return map[jobKey(pack)] || "saved";
}

function setStatus(map, pack, status) {
  map[jobKey(pack)] = status;
  saveStatusMap(map);
}

function saveScrapeFilters(filters) {
  localStorage.setItem(FILTER_PREFS_KEY, JSON.stringify(filters));
}
function loadScrapeFilters() {
  try {
    const raw = localStorage.getItem(FILTER_PREFS_KEY);
    return raw ? JSON.parse(raw) : { hours_old: 168 };
  } catch {
    return { hours_old: 168 };
  }
}
function readScrapeFilters() {
  // Scraping is intentionally broad: profile role + how far back. Seniority is
  // NOT applied at scrape time — it's a Job Listings refinement so you never
  // have to re-fetch to change levels.
  const hours = Number($("filter-hours")?.value || 168);
  const filters = { hours_old: hours, seniority: "any" };
  saveScrapeFilters(filters);
  return filters;
}
function applyScrapeFiltersToUi() {
  const prefs = loadScrapeFilters();
  if ($("filter-hours")) $("filter-hours").value = String(prefs.hours_old || 168);
}

/* ---------------- fetch status + progress ---------------- */
function getLastFetch() {
  const v = Number(localStorage.getItem(LAST_FETCH_KEY) || 0);
  return Number.isFinite(v) ? v : 0;
}
function setLastFetch(ts) {
  localStorage.setItem(LAST_FETCH_KEY, String(ts));
}
function formatRelative(ts) {
  const t = typeof ts === "number" ? ts : Date.parse(ts || "");
  if (!t || Number.isNaN(t)) return "recently";
  const min = Math.floor((Date.now() - t) / 60000);
  if (min < 1) return "just now";
  if (min < 60) return `${min} min ago`;
  const hr = Math.floor(min / 60);
  if (hr < 24) return `${hr} hour${hr === 1 ? "" : "s"} ago`;
  const d = Math.floor(hr / 24);
  return `${d} day${d === 1 ? "" : "s"} ago`;
}
function setFetchBusy(busy) {
  for (const id of ["btn-scrape", "btn-boost"]) {
    const b = $(id);
    if (b) b.disabled = busy;
  }
}

/** Single, de-duplicated fetch status: a row of chips (count · range · when). */
function fetchChip(text, kind = "") {
  return `<span class="fetch-chip ${kind}">${escapeHtml(text)}</span>`;
}
function refreshFetchSummary() {
  const el = $("fetch-summary");
  if (!el) return;
  const status = state.cacheStatus;
  if (!status?.cache_exists) {
    el.innerHTML = fetchChip("No jobs fetched yet", "muted");
    return;
  }
  const count = status.cached_count ?? state.packs.length;
  const when = status.fetched_at || getLastFetch();
  const chips = [fetchChip(`${count} jobs`, "strong")];
  if (status.hours_old) chips.push(fetchChip(`last ${hoursLabel(status.hours_old)}`));
  chips.push(fetchChip(`fetched ${formatRelative(when)}`));
  el.innerHTML = chips.join("");
}
// kept name for the on-load + interval call sites
function updateFetchButton() {
  refreshFetchSummary();
}

/* ---- animated fetch progress stepper ---- */
const FETCH_STEPS = ["scrape", "compose", "pack"];
function setFetchStep(step) {
  const idx = FETCH_STEPS.indexOf(step);
  const fill = $("fetch-progress-fill");
  if (fill) fill.style.width = `${Math.round(((idx + 0.5) / FETCH_STEPS.length) * 100)}%`;
  document.querySelectorAll("#fetch-progress .fetch-steps li").forEach((li) => {
    const i = FETCH_STEPS.indexOf(li.dataset.step);
    li.classList.toggle("done", i < idx);
    li.classList.toggle("active", i === idx);
  });
}
function showFetchProgress() {
  const box = $("fetch-progress");
  if (box) { box.classList.add("running"); show(box); }
  setFetchStep("scrape");
}
function completeFetchProgress() {
  const fill = $("fetch-progress-fill");
  if (fill) fill.style.width = "100%";
  const box = $("fetch-progress");
  if (box) box.classList.remove("running");
  document.querySelectorAll("#fetch-progress .fetch-steps li").forEach((li) => {
    li.classList.remove("active");
    li.classList.add("done");
  });
}
function hideFetchProgress() { hide($("fetch-progress")); }

/* ---------------- seniority + recency (client-side listing filters) ---------------- */
const _SENIOR_MARKERS = ["senior", "sr.", "sr ", "lead", "principal", "staff", "director", "head of", "architect", "manager"];
const _INTERN_MARKERS = ["intern", "internship", "trainee", "co-op", "co op"];
const _JUNIOR_MARKERS = ["junior", "jr.", "jr ", "entry level", "entry-level", "graduate", "fresher", "associate"];
function classifySeniority(title) {
  const t = String(title || "").toLowerCase();
  const has = (arr) => arr.some((m) => t.includes(m));
  if (has(_INTERN_MARKERS)) return "intern";
  if (has(_SENIOR_MARKERS)) return "senior";
  if (has(_JUNIOR_MARKERS)) return "junior";
  return "mid";
}
function withinHours(publishedAt, hours) {
  if (!hours) return true;
  const t = Date.parse(publishedAt || "");
  if (Number.isNaN(t)) return false;
  return Date.now() - t <= hours * 60 * 60 * 1000;
}

function parseProxies(raw) {
  return String(raw || "")
    .split(/[\n,]+/)
    .map((p) => p.trim())
    .filter(Boolean);
}

/* ---------------- formatting helpers ---------------- */
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

const AVATAR_COLORS = ["#6366f1", "#3b82f6", "#a855f7", "#ec4899", "#f59e0b", "#10b981", "#ef4444", "#0ea5e9"];
function companyColor(name) {
  const s = String(name || "?");
  let h = 0;
  for (let i = 0; i < s.length; i += 1) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return AVATAR_COLORS[h % AVATAR_COLORS.length];
}
function initials(name) {
  const parts = String(name || "?").trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "?";
  return (parts[0][0] + (parts[1]?.[0] || "")).toUpperCase();
}
function setUserMenu(profile) {
  const btn = $("user-menu-btn");
  const nameEl = $("user-menu-name");
  const avatar = $("user-avatar");
  if (!btn) return;
  const name = profile?.name?.trim() || "Set up profile";
  if (nameEl) nameEl.textContent = name;
  if (avatar) avatar.textContent = initials(name);
  show(btn);
  updateProfileBanner(profile);
  const roleLabel = $("scrape-role-label");
  if (roleLabel) {
    const role = state.catalog?.roles?.find(
      (r) => r.search_term?.toLowerCase() === String(profile?.search_term || "").toLowerCase(),
    )?.label;
    roleLabel.textContent = role || profile?.search_term || "your profile role";
  }
}

function updateProfileBanner(profile) {
  const banner = $("profile-required-banner");
  if (!banner) return;
  if (isProfileComplete(profile)) hide(banner);
  else show(banner);
}

const VIEW_TITLES = {
  dashboard: ["Dashboard", "Your job search at a glance"],
  jobs: ["Job Listings", "Filter and apply to roles tailored to you"],
  resume: ["Resume", "Your base Overleaf resume"],
  settings: ["Settings", "Fetch fresh jobs when needed"],
};

function switchView(view) {
  for (const el of document.querySelectorAll(".view")) hide(el);
  show($(`view-${view}`));
  for (const btn of document.querySelectorAll(".nav-item")) {
    btn.classList.toggle("active", btn.dataset.view === view);
  }
  const [title, sub] = VIEW_TITLES[view] || VIEW_TITLES.dashboard;
  $("page-title").textContent = title;
  $("page-subtitle").textContent = sub;
}

/* ---------------- profile modal ---------------- */
async function openProfileModal(anna, { forced = false } = {}) {
  state.profileModalForced = forced;
  hide($("profile-form-error"));
  try {
    const profile = await getProfile(anna);
    state.profile = profile;
    fillProfileForm($("profile-form"), profile, state.catalog);
    populateRoleSelect($("input-role"), state.catalog, $("input-role-id")?.value);
    populateDomainSelect($("input-domain"), state.catalog, profile?.domain);
  } catch {
    fillProfileForm($("profile-form"), null, state.catalog);
  }
  show($("profile-modal"));
  $("input-name")?.focus();
}

function closeProfileModal() {
  if (state.profileModalForced && !isProfileComplete(state.profile)) {
    onStep("Save your profile before continuing.", true);
    return;
  }
  hide($("profile-modal"));
  state.profileModalForced = false;
}

function renderProfileSummary(profile) {
  const el = $("profile-summary");
  if (!el) return;
  if (!isProfileComplete(profile)) {
    el.innerHTML = '<p class="hint">Profile incomplete — click your name (top right) or Edit profile.</p>';
    return;
  }
  const skills = Array.isArray(profile.target_skills) ? profile.target_skills.join(", ") : profile.target_skills || "—";
  const roleLabel = state.catalog?.roles?.find(
    (r) => r.search_term?.toLowerCase() === String(profile.search_term).toLowerCase(),
  )?.label;
  el.innerHTML = `
    <dl>
      <dt>Name</dt><dd>${escapeHtml(profile.name || "—")}</dd>
      <dt>Role</dt><dd>${escapeHtml(roleLabel || profile.search_term || "—")}</dd>
      <dt>Location</dt><dd>${escapeHtml(profile.location || "India")}</dd>
      <dt>Skills</dt><dd>${escapeHtml(skills)}</dd>
    </dl>`;
}

function renderResumeView(profile) {
  const el = $("resume-summary");
  if (!el) return;
  if (!isProfileComplete(profile)) {
    el.innerHTML = '<p class="hint">No resume yet — open your profile and paste your Overleaf .tex.</p>';
    return;
  }
  const tex = String(profile.resume_tex || "");
  const skills = Array.isArray(profile.target_skills) ? profile.target_skills.length : 0;
  el.innerHTML = `
    <dl>
      <dt>Name</dt><dd>${escapeHtml(profile.name || "—")}</dd>
      <dt>Document class</dt><dd>${tex.includes("\\documentclass{resume}") ? "resume.cls (Overleaf)" : "custom"}</dd>
      <dt>LaTeX length</dt><dd>${tex.length.toLocaleString()} chars</dd>
      <dt>Target skills</dt><dd>${skills} skills</dd>
    </dl>`;
}

/* ---------------- KPIs + dashboard ---------------- */
// Counts come from the saved status map (every job you've ever marked), NOT just
// the current fetch. So applying to a 30-day-old job and then fetching the last
// 24h keeps your Applied/Interview/Offer totals intact — the dashboard reflects
// everything you've done with the app, not only what's currently listed.
function computeKpis(packs, statusMap) {
  let applications = 0, interviews = 0, offers = 0, rejected = 0;
  for (const s of Object.values(statusMap || {})) {
    if (s && s !== "saved") applications += 1;
    if (s === "interview") interviews += 1;
    if (s === "offer") offers += 1;
    if (s === "rejected") rejected += 1;
  }
  return { applications, interviews, offers, rejected, total: packs.length };
}

function formatSources(bySource) {
  if (!bySource || typeof bySource !== "object") return "—";
  return Object.entries(bySource).map(([k, v]) => `${k}: ${v}`).join(" · ") || "—";
}

function renderDashboard(packs, statusMap, scrape) {
  const kpi = computeKpis(packs, statusMap);
  $("kpi-applications").textContent = String(kpi.applications);
  $("kpi-interviews").textContent = String(kpi.interviews);
  $("kpi-offers").textContent = String(kpi.offers);
  $("kpi-ready").textContent = String(kpi.total);
  $("kpi-applications-trend").textContent = kpi.rejected ? `${kpi.rejected} rejected` : "\u00a0";
  $("kpi-interviews-trend").textContent = kpi.interviews ? "active" : "\u00a0";
  $("kpi-offers-trend").textContent = kpi.offers ? "🎉" : "\u00a0";
  $("kpi-ready-trend").textContent = kpi.total ? "tailored" : "\u00a0";

  renderProfileSummary(state.profile);

  const src = $("source-list");
  if (src) {
    const jobCount = scrape?.count ?? packs.length;
    const query = scrape?.search_term || state.profile?.search_term || "—";
    src.innerHTML = `
      <li><span><strong>Free APIs</strong> · Remotive, RemoteOK, Arbeitnow</span>
        <span class="badge ${jobCount > 0 ? "active" : "idle"}">${jobCount > 0 ? "ACTIVE" : "IDLE"}</span></li>
      <li><span><strong>Indeed + Google</strong> · ${escapeHtml(query)}</span>
        <span class="badge ${jobCount > 0 ? "active" : "idle"}">${jobCount > 0 ? "ACTIVE" : "IDLE"}</span></li>`;
  }

  const chart = $("pipeline-chart");
  if (chart) {
    const stages = [
      { label: "Ready", count: kpi.total, color: "#6366f1" },
      { label: "Applied", count: kpi.applications, color: "#3b82f6" },
      { label: "Interview", count: kpi.interviews, color: "#f59e0b" },
      { label: "Offer", count: kpi.offers, color: "#22c55e" },
    ];
    const max = Math.max(...stages.map((s) => s.count), 1);
    chart.innerHTML = stages.map((s) => `
      <div class="pipe-col">
        <div class="pipe-count">${s.count}</div>
        <div class="pipe-bar" style="height:${Math.max(12, (s.count / max) * 120)}px;background:${s.color}"></div>
        <div class="pipe-label">${s.label}</div>
      </div>`).join("");
  }

  // recent applications table on dashboard (top 6)
  const wrap = $("dash-table-wrap");
  if (wrap) {
    if (!packs.length) {
      wrap.innerHTML = "";
      show($("dash-empty"));
    } else {
      hide($("dash-empty"));
      wrap.innerHTML = buildJobTable(packs.slice(0, 6), statusMap, { compact: true });
      wireTableEvents(wrap, packs, statusMap);
    }
  }
}

/* ---------------- job table ---------------- */
function statusSelectHtml(pack, statusMap) {
  const cur = getStatus(statusMap, pack);
  const opts = STATUSES.map(
    (s) => `<option value="${s}" ${s === cur ? "selected" : ""}>${STATUS_LABEL[s]}</option>`,
  ).join("");
  return `<select class="status-select status-${cur}" data-key="${escapeAttr(jobKey(pack))}">${opts}</select>`;
}

function buildJobTable(packs, statusMap, { compact = false } = {}) {
  const rows = packs.map((pack) => {
    const idx = pack.job_index ?? 0;
    const company = pack.company || "—";
    const locCell = compact ? "" : `<td class="muted-cell">${escapeHtml(pack.location || "—")}</td>`;
    const srcCell = compact ? "" : `<td><span class="source-tag">${escapeHtml(pack.source || "—")}</span></td>`;
    return `
      <tr data-index="${idx}">
        <td>
          <div class="company-cell">
            <div class="company-avatar" style="background:${companyColor(company)}">${escapeHtml(initials(company))}</div>
            <span class="company-name">${escapeHtml(company)}</span>
          </div>
        </td>
        <td class="position-cell">${escapeHtml(pack.job_title || "Untitled")}</td>
        ${locCell}
        <td>${statusSelectHtml(pack, statusMap)}</td>
        ${srcCell}
        <td>
          <div class="row-actions">
            <a class="btn small primary" href="${escapeAttr(pack.apply_url || "#")}" target="_blank" rel="noopener">Open &amp; Apply</a>
            <button type="button" class="btn small secondary btn-pdf" data-index="${idx}">Preview PDF</button>
          </div>
        </td>
      </tr>`;
  }).join("");

  const head = compact
    ? `<th>Company</th><th>Position</th><th>Status</th><th>Action</th>`
    : `<th>Company</th><th>Position</th><th>Location</th><th>Status</th><th>Source</th><th>Action</th>`;

  return `<table class="job-table"><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table>`;
}

function wireTableEvents(container, allPacks, statusMap) {
  const anna = state.anna;
  container.querySelectorAll(".status-select").forEach((sel) => {
    sel.addEventListener("change", () => {
      const key = sel.dataset.key;
      const status = sel.value;
      statusMap[key] = status;
      saveStatusMap(statusMap);
      sel.className = `status-select status-${status}`;
      renderDashboard(state.packs, statusMap, state.scrape);
    });
  });
  container.querySelectorAll(".btn-pdf").forEach((btn) => {
    btn.addEventListener("click", () => {
      const idx = Number(btn.dataset.index);
      const pack = allPacks.find((p) => (p.job_index ?? 0) === idx) || { job_index: idx };
      exportResumePdf(anna, pack, btn);
    });
  });
}

function renderListings(packs, statusMap) {
  const wrap = $("jobs-table-wrap");
  const empty = $("empty-state");
  const meta = $("jobs-meta");
  if (!wrap) return;

  const search = ($("job-filter")?.value || "").toLowerCase();
  let visible = packs || [];
  if (state.statusFilter !== "all") {
    visible = visible.filter((p) => getStatus(statusMap, p) === state.statusFilter);
  }
  if (state.listSeniority !== "all") {
    visible = visible.filter((p) => classifySeniority(p.job_title) === state.listSeniority);
  }
  if (state.listHours) {
    visible = visible.filter((p) => withinHours(p.published_at, state.listHours));
  }
  if (search) {
    visible = visible.filter((p) =>
      `${p.job_title} ${p.company} ${p.source || ""}`.toLowerCase().includes(search),
    );
  }

  if (!visible.length) {
    wrap.innerHTML = "";
    show(empty);
    if (meta) meta.textContent = packs?.length ? "0 of " + packs.length : "";
    return;
  }
  hide(empty);
  if (meta) meta.textContent = `${visible.length} of ${packs.length} job${packs.length === 1 ? "" : "s"}`;
  wrap.innerHTML = buildJobTable(visible, statusMap);
  wireTableEvents(wrap, packs, statusMap);
}

function renderAll() {
  renderDashboard(state.packs, state.statusMap, state.scrape);
  renderListings(state.packs, state.statusMap);
}

/* ---------------- cache status ---------------- */
async function loadCacheStatus(anna) {
  try {
    const status = await invokeTool(anna, "scraper", { action: "cache_status" });
    state.cacheStatus = status;
    refreshFetchSummary();
    if (status.latest_exists && status.filtered_count != null) {
      state.scrape = {
        count: status.filtered_count,
        count_before_seniority_filter: status.count_before_seniority_filter ?? status.cached_count,
        seniority_filter: status.seniority_filter,
        fetched_at: status.fetched_at,
        search_term: status.search_term,
      };
    }
    return status;
  } catch {
    return null;
  }
}

/* ---------------- PDF preview (PDF.js → canvas) ---------------- */
async function renderPdfToCanvas(base64) {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
  const pdf = await pdfjsLib.getDocument({ data: bytes }).promise;
  const container = $("pdf-pages");
  container.innerHTML = "";
  const scale = 1.6;
  for (let n = 1; n <= pdf.numPages; n += 1) {
    const page = await pdf.getPage(n);
    const viewport = page.getViewport({ scale });
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    const ratio = window.devicePixelRatio || 1;
    canvas.width = Math.floor(viewport.width * ratio);
    canvas.height = Math.floor(viewport.height * ratio);
    canvas.style.width = `${Math.floor(viewport.width)}px`;
    canvas.style.height = `${Math.floor(viewport.height)}px`;
    container.appendChild(canvas);
    await page.render({ canvasContext: ctx, viewport, transform: ratio !== 1 ? [ratio, 0, 0, ratio, 0, 0] : undefined }).promise;
  }
}

function closePdfModal() {
  hide($("pdf-modal"));
  $("pdf-pages").innerHTML = "";
}

async function exportResumePdf(anna, pack, btn) {
  const label = btn?.textContent;
  if (btn) { btn.disabled = true; btn.textContent = "Building…"; }
  hide($("pdf-modal-error"));
  $("pdf-modal-title").textContent = pack.base ? "Base resume preview" : `${pack.job_title || "Resume"} — ${pack.company || ""}`;
  $("pdf-saved-note").textContent = "Compiling LaTeX…";
  $("pdf-pages").innerHTML = "";
  show($("pdf-modal"));
  try {
    const args = { action: "compile_pdf", to_downloads: true };
    if (pack.base) args.base = true;
    else if (pack.resume_tex_path) args.tex_path = pack.resume_tex_path;
    else if (pack.job_index != null) args.job_index = pack.job_index;
    else throw new Error("No resume yet — click Fetch jobs first.");
    if (pack.job_title) args.job_title = pack.job_title;
    if (pack.company) args.company = pack.company;

    const data = await invokeTool(anna, "composer", args, PDF_TIMEOUT_MS);
    if (!data?.pdf_base64) throw new Error("PDF compile returned empty data.");
    await renderPdfToCanvas(data.pdf_base64);
    const saved = data.downloads_path || data.pdf_path;
    $("pdf-saved-note").textContent = saved
      ? `Saved to ${saved.replace(/^.*\/(?=Downloads\/)/, "")} · use Print to save another copy`
      : "Use Print / Save as PDF to download";
    onStep(saved ? `Resume saved: ${saved}` : "Resume preview ready.", false);
    if (btn) { btn.textContent = "✓ Previewed"; setTimeout(() => { btn.textContent = label; btn.disabled = false; }, 2000); }
  } catch (err) {
    const msg = friendlyError(err);
    $("pdf-modal-error").textContent = msg;
    show($("pdf-modal-error"));
    $("pdf-saved-note").textContent = "Couldn't build the PDF";
    onStep(msg, true);
    if (btn) { btn.textContent = "Failed"; setTimeout(() => { btn.textContent = label; btn.disabled = false; }, 4000); }
  }
}

/* ---------------- profile ---------------- */
async function getProfile(anna) {
  return invokeTool(anna, "profile", { action: "get" });
}

async function saveProfile(anna, form) {
  const name = form.name.value.trim();
  const latex = form.latex.value.trim();
  const searchTerm = form.search_term.value.trim();
  const skills = form.target_skills.value.trim();
  if (!name) throw new Error("Name is required.");
  if (!latex) throw new Error("Paste your full Overleaf resume (.tex).");
  if (!searchTerm) throw new Error("Indeed search query is required.");
  if (!skills) throw new Error("Target skills are required.");

  return invokeTool(anna, "profile", {
    action: "save",
    name,
    domain: form.domain.value,
    seniority: form.seniority.value,
    years_experience: Number(form.years.value) || 0,
    location: form.location.value.trim() || "India",
    search_term: searchTerm,
    target_skills: skills,
    resume_latex: latex,
  });
}

/* ---------------- pipeline ---------------- */
function hoursLabel(hours) {
  const map = { 24: "24 hours", 48: "48 hours", 72: "3 days", 168: "7 days", 336: "14 days", 720: "30 days" };
  return map[Number(hours)] || `${hours} hours`;
}

async function fetchJobs(anna, { mode = "free", proxies = [], filters = {} } = {}) {
  const args = {
    action: "scrape",
    use_profile: true,
    mode,
    results_wanted: SCRAPE_RESULTS_WANTED,
    hours_old: Number(filters.hours_old || 168),
    seniority_filter: "any", // scrape broad; refine seniority in Job Listings
    include_free_apis: true,
    persist: true,
    max_response_jobs: 5,
  };
  if (mode === "boost") {
    if (!proxies.length) throw new Error("Boost mode requires at least one proxy.");
    args.proxies = proxies;
  }
  return invokeTool(anna, "scraper", args, SCRAPE_TIMEOUT_MS);
}

/** One button does it all: scrape broadly, tailor a resume per job, build packs. */
async function runFetch(anna, scrapeOptions = {}) {
  const profile = await getProfile(anna);
  if (!isProfileComplete(profile)) {
    await openProfileModal(anna, { forced: true });
    throw new Error("Complete your profile first.");
  }
  state.profile = profile;
  setUserMenu(profile);

  const filters = readScrapeFilters();
  setFetchStep("scrape");
  onStep(`Fetching jobs from the last ${hoursLabel(filters.hours_old)}…`, false);
  const scrape = await fetchJobs(anna, { ...scrapeOptions, filters });
  state.scrape = scrape;
  if (!scrape.count) {
    throw new Error("No jobs found. Try a wider date range or a shorter role in your profile.");
  }

  setFetchStep("compose");
  onStep(`Fetched ${scrape.count} jobs. Tailoring your resume to each…`, false);
  await invokeTool(anna, "composer", { action: "compose_all" }, COMPOSE_TIMEOUT_MS);
  setFetchStep("pack");
  onStep("Preparing your job list…", false);
  await invokeTool(anna, "pack", { action: "prepare_all" });
  state.packs = await fetchAllPacks(anna);

  completeFetchProgress();
  setLastFetch(Date.now());
  await loadCacheStatus(anna);
  onStep(
    `Done — ${state.packs.length} jobs ready. Refine them by seniority or date in Job Listings.`,
    false,
  );
  return scrape;
}

function onStep(msg, isError = false) {
  const el = $("pipeline-status");
  if (!el) return;
  el.textContent = msg;
  el.classList.toggle("error", isError);
}

/* ---------------- main ---------------- */
async function main() {
  state.statusMap = loadStatusMap();
  let anna;
  try {
    anna = await AnnaAppRuntime.connect();
    state.anna = anna;
    await anna.window.set_title({ title: "ResuMatch" });
  } catch {
    $("boot-screen").innerHTML =
      '<div class="boot-card"><h2>ResuMatch</h2><p>Couldn\'t connect to the workspace. Please reopen this app from your dashboard.</p></div>';
    return;
  }

  state.catalog = await loadJobCatalog();
  populateRoleSelect($("input-role"), state.catalog);
  populateDomainSelect($("input-domain"), state.catalog);
  applyScrapeFiltersToUi();
  updateFetchButton();
  setInterval(updateFetchButton, 60_000);

  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (btn.dataset.nav === "profile") { openProfileModal(anna); return; }
      if (btn.dataset.view) {
        switchView(btn.dataset.view);
        if (btn.dataset.view === "resume") renderResumeView(state.profile);
      }
    });
  });

  $("btn-view-all-jobs")?.addEventListener("click", () => switchView("jobs"));

  $("input-role")?.addEventListener("change", (e) => {
    const role = findRole(state.catalog, e.target.value);
    if (role) applyRoleToForm($("profile-form"), role);
  });

  $("user-menu-btn")?.addEventListener("click", () => openProfileModal(anna));
  $("btn-edit-profile-dash")?.addEventListener("click", () => openProfileModal(anna));
  $("btn-edit-resume")?.addEventListener("click", () => openProfileModal(anna));
  $("btn-edit-profile-settings")?.addEventListener("click", () => openProfileModal(anna));
  $("btn-open-profile-banner")?.addEventListener("click", () => openProfileModal(anna, { forced: true }));
  $("btn-close-profile")?.addEventListener("click", closeProfileModal);
  $("btn-cancel-profile")?.addEventListener("click", closeProfileModal);
  $("profile-modal-backdrop")?.addEventListener("click", closeProfileModal);

  $("btn-close-pdf")?.addEventListener("click", closePdfModal);
  $("pdf-modal-backdrop")?.addEventListener("click", closePdfModal);
  $("btn-print-pdf")?.addEventListener("click", () => window.print());

  $("btn-preview-base")?.addEventListener("click", () => {
    if (!isProfileComplete(state.profile)) { openProfileModal(anna, { forced: true }); return; }
    exportResumePdf(anna, { base: true, job_title: "Base resume", company: state.profile?.name || "" }, $("btn-preview-base"));
  });

  $("profile-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    hide($("profile-form-error"));
    const btn = e.target.querySelector('button[type="submit"]');
    btn.disabled = true;
    try {
      const data = await saveProfile(anna, e.target);
      state.profile = data;
      state.profileModalForced = false;
      setUserMenu(data);
      renderProfileSummary(data);
      renderResumeView(data);
      hide($("profile-modal"));
      onStep("Profile saved.");
    } catch (err) {
      $("profile-form-error").textContent = err.message;
      show($("profile-form-error"));
    } finally {
      btn.disabled = false;
    }
  });

  $("filter-hours")?.addEventListener("change", () => {
    readScrapeFilters();
    onStep("Date range applies on your next Fetch jobs.", false);
  });
  $("job-filter")?.addEventListener("input", () => renderListings(state.packs, state.statusMap));
  $("list-seniority")?.addEventListener("change", (e) => {
    state.listSeniority = e.target.value;
    renderListings(state.packs, state.statusMap);
  });
  $("list-hours")?.addEventListener("change", (e) => {
    state.listHours = Number(e.target.value) || 0;
    renderListings(state.packs, state.statusMap);
  });

  document.querySelectorAll(".status-tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".status-tab").forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      state.statusFilter = tab.dataset.status;
      renderListings(state.packs, state.statusMap);
    });
  });

  $("btn-scrape")?.addEventListener("click", async () => {
    setFetchBusy(true);
    showFetchProgress();
    try {
      await runFetch(anna, { mode: "free" });
      renderAll();
      setTimeout(() => switchView("jobs"), 700);
    } catch (err) {
      hideFetchProgress();
      onStep(friendlyError(err), true);
    } finally {
      setFetchBusy(false);
      updateFetchButton();
      setTimeout(hideFetchProgress, 1600);
    }
  });

  $("boost-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    hide($("boost-error"));
    setFetchBusy(true);
    showFetchProgress();
    try {
      const proxies = parseProxies($("input-proxies")?.value);
      await runFetch(anna, { mode: "boost", proxies });
      renderAll();
      setTimeout(() => switchView("jobs"), 700);
    } catch (err) {
      hideFetchProgress();
      const msg = friendlyError(err);
      $("boost-error").textContent = msg;
      show($("boost-error"));
      onStep(msg, true);
    } finally {
      setFetchBusy(false);
      updateFetchButton();
      setTimeout(hideFetchProgress, 1600);
    }
  });

  hide($("boot-screen"));
  show($("app"));

  try {
    const profile = await getProfile(anna);
    state.profile = profile;
    setUserMenu(profile);
    switchView("dashboard");

    if (!isProfileComplete(profile)) {
      await openProfileModal(anna, { forced: true });
    } else {
      await loadCacheStatus(anna);
      try {
        state.packs = await fetchAllPacks(anna);
      } catch {
        state.packs = [];
      }
    }
    renderAll();
  } catch {
    switchView("dashboard");
    await openProfileModal(anna, { forced: true });
  }
}

main();
