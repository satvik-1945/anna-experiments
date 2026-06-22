# ResuMatch — Hackathon Demo Video Script

**Target length:** 2–3 minutes  
**Format:** Screen recording + light voiceover  
**Goal:** Show a focused, working Anna App — not a slide deck.

---

## 0:00 — Hook (10 sec)

**On screen:** ResuMatch dashboard (KPI cards visible).

**Say:**
> "Job hunting is repetitive — you scrape the same boards, rewrite the same resume, and lose track of what you applied to. ResuMatch is an Anna App that does the boring work locally: fetch jobs once, tailor your resume per role, and track your pipeline — you still click Apply."

---

## 0:10 — What it is + who it's for (15 sec)

**On screen:** Sidebar: Dashboard → Job Listings → Profile → Resume → Settings.

**Say:**
> "ResuMatch is for anyone applying manually — students, career switchers, engineers who want control over every submission. It runs on Anna: four Executas handle profile, scraping, resume tailoring, and apply packs, with a dashboard UI you open inside Anna."

---

## 0:25 — Profile (30 sec)

**On screen:** Click your name → Profile modal.

**Say:**
> "First I set up my profile once — name, target role like Software Engineer, skills, and my full Overleaf LaTeX resume. This is the source of truth. The scraper uses my role; the composer only changes the Skills section per job — nothing is invented."

**Do:** Show role dropdown, skills field, scroll a bit of `.tex`, click **Save profile**.

---

## 0:55 — Fetch jobs (45 sec)

**On screen:** Settings → Fetch jobs card.

**Say:**
> "Fetching is the one expensive step. I pick how far back to look — say last 7 days — and hit Fetch jobs. ResuMatch scrapes free APIs plus Indeed and Google, then tailors a resume for every result and builds my listing. I don't need to fetch again just to change seniority or date — I refine in Job Listings."

**Do:** Click **Fetch jobs**. Let the progress stepper run (Searching → Tailoring → Preparing). Land on Job Listings when done.

---

## 1:40 — Job Listings + filters (40 sec)

**On screen:** Job Listings table.

**Say:**
> "Here are my ready-to-apply roles. I can filter by seniority and posted date without re-scraping — so if I fetched 30 days of jobs, I can narrow to the last 24 hours instantly. Status tabs track Saved, Applied, Interview, Offer. The dashboard remembers everything I've marked, even if a job drops off the next fetch."

**Do:** Change **Seniority** to Junior, then **Posted within** to Last 48 hours. Show result count updating. Change one job status to **Applied**.

---

## 2:20 — Tailored PDF (35 sec)

**On screen:** Click **Preview PDF** on one row.

**Say:**
> "For each job I get a tailored resume PDF — compiled locally with Tectonic, previewed in-app with PDF.js, and saved to Downloads. I review it, print or save, then open the real apply link and submit myself."

**Do:** Wait for PDF preview modal. Brief scroll. Close modal.

---

## 2:55 — Dashboard truth (20 sec)

**On screen:** Dashboard.

**Say:**
> "The dashboard is my honest history — applications, interviews, offers — driven by what I've actually marked, not just what's in today's fetch."

**Do:** Point at KPI cards after the Applied status change.

---

## 3:15 — Anna + AI angle (25 sec)

**On screen:** Optionally show Anna chat mentioning `#resumatch` or opening the app from Anna.

**Say:**
> "ResuMatch is built on Anna's platform layer — Executa tools for scraping and LaTeX, permissions, local dev harness, and a path to the App Store. The intelligence is in matching your real resume skills to each job description and preparing a pack you can trust — not auto-submitting for you."

---

## 3:40 — Close (10 sec)

**On screen:** Settings summary chips (`524 jobs · last 7 days · fetched …`).

**Say:**
> "ResuMatch — scrape once, tailor many, apply with confidence. Built on Anna. Thanks."

---

## Recording checklist

- [ ] Use a real or realistic profile (name, role, short `.tex` sample)
- [ ] Pre-fetch once before recording so the demo path is fast; re-fetch live only if time allows
- [ ] Hide Boost scrape section unless you want to mention "coming later"
- [ ] Window size ~900×950 so the sidebar and table look clean
- [ ] No terminal visible — Anna UI only

## B-roll shots (optional inserts)

1. Progress stepper during fetch (Settings)
2. PDF preview modal (canvas render)
3. Status dropdown changing to Applied
4. Dashboard KPIs updating
