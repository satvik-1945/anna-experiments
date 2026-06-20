# Job Scraper Catalog — Step 1 Research

> **Project goal:** Build an Anna App that *suggests* fresh jobs (last 24h) for manual application — not auto-apply.  
> **Success bar for Step 1:** A scraper/API combo that reliably surfaces **100–200 relevant jobs in the last 24 hours** during local testing.

This catalog lists every scraper, API, and managed tool worth experimenting with. We will test them one by one and record results in `EXPERIMENT_LOG.md`.

---

## How to read this catalog

| Column | Meaning |
|--------|---------|
| **Type** | `OSS` = open-source library/repo, `API` = official REST API, `Managed` = Apify/SaaS actor, `Hybrid` = wraps scrapers behind an API |
| **Auth** | What credentials you need (`None`, `API key`, `LinkedIn login`, `Apify token`) |
| **LinkedIn?** | Whether it targets LinkedIn specifically |
| **Posts?** | Whether it can scrape LinkedIn *posts* (e.g. `#hiring`, `#SDE`) vs formal job listings |
| **24h filter** | Whether it supports filtering by posting date (last 24 hours) |
| **Priority** | Suggested experiment order for our use case (`P0` = try first) |

---

## Evaluation criteria (our bar)

Before green-lighting any source for the Executa:

1. **Volume:** ≥ 100 jobs in a single run for a broad SWE query (or combined across sources)
2. **Freshness:** Majority posted within last 24 hours (`hours_old=24`, `date_posted=24hr`, etc.)
3. **Structured output:** Title, company, location, description/JD, apply URL or contact email
4. **Reliability:** No CAPTCHA blocks, no account bans, repeatable locally
5. **Cost:** Free tier or low enough for hackathon/demo use
6. **Anna fit:** Callable from a Python Executa plugin (HTTP client, subprocess, or Apify SDK)

---

## Category A — Multi-board Python libraries (highest priority)

These scrape several job boards from one function call. Best starting point because one library covers LinkedIn + Indeed + Google Jobs + more.

### 1. JobSpy ⭐ P0

| | |
|---|---|
| **Repo** | https://github.com/speedyapply/JobSpy |
| **Install** | `pip install -U python-jobspy` |
| **Docs** | https://speedyapply-jobspy.mintlify.app/introduction |
| **Type** | OSS (Python) |
| **Auth** | None (proxies recommended for LinkedIn) |
| **Boards** | LinkedIn, Indeed, Glassdoor, Google Jobs, ZipRecruiter, Bayt, Naukri, BDJobs |
| **24h filter** | ✅ `hours_old=24` |
| **LinkedIn posts?** | ❌ Job listings only |

**Why try first:** Most popular OSS job aggregator (~3.6k stars). Single `scrape_jobs()` call returns a Pandas DataFrame. Indeed is reliable; LinkedIn rate-limits ~page 10/IP without proxies.

```python
from jobspy import scrape_jobs
jobs = scrape_jobs(
    site_name=["indeed", "linkedin", "google"],
    search_term="software engineer",
    location="United States",
    results_wanted=200,
    hours_old=24,
    country_indeed="USA",
)
```

**Known issues:** LinkedIn is the most restrictive board; proxies are basically required at scale. Easy Apply filter no longer works.

---

### 2. sankeer28/Job-API (JobSpy + public APIs wrapper) — P0

| | |
|---|---|
| **Repo** | https://github.com/sankeer28/Job-API |
| **Type** | Hybrid (Vercel serverless API wrapping JobSpy + free APIs) |
| **Auth** | None (self-host) |
| **Boards** | Indeed, LinkedIn, Naukri (via JobSpy) + RemoteOK, Arbeitnow, Remotive, Jobicy (public APIs) |

**Why try:** Pre-built aggregation layer — same JobSpy under the hood but also pulls free remote-job APIs in one request. Good reference architecture for our Executa.

---

## Category B — LinkedIn job listing scrapers (OSS)

### 3. joeyism/linkedin_scraper — P1

| | |
|---|---|
| **Repo** | https://github.com/joeyism/linkedin_scraper |
| **PyPI** | https://pypi.org/project/linkedin-scraper/ |
| **Type** | OSS (Python, Playwright) |
| **Auth** | LinkedIn session cookies (`session.json`) |
| **24h filter** | ⚠️ Via search params, not explicit API param |
| **LinkedIn posts?** | ✅ Company posts supported; job search via `JobSearchScraper` |

**Notes:** 4k+ stars, actively maintained (v3.x, async Playwright). Requires browser automation + saved login session. More setup than JobSpy but richer data (profiles, companies, posts).

---

### 4. open-linkedin-jobs (Node.js) — P2

| | |
|---|---|
| **Repo** | https://github.com/Hyraze/open-linkedin-jobs |
| **npm** | https://www.npmjs.com/package/open-linkedin-jobs |
| **Type** | OSS (TypeScript/Node) |
| **Auth** | None |
| **24h filter** | ✅ `dateSincePosted: '24hr'` |

**Notes:** Lightweight HTTP + Cheerio parser. No browser. Good if we want a Node sidecar, but our Anna Executa will likely be Python.

---

### 5. tomquirk/linkedin-api (Voyager API wrapper) — P2

| | |
|---|---|
| **Repo** | https://github.com/tomquirk/linkedin-api |
| **PyPI** | https://pypi.org/project/linkedin-api/ |
| **Docs** | https://linkedin-api.readthedocs.io |
| **Type** | OSS (Python) |
| **Auth** | LinkedIn email + password (uses Voyager internal API) |
| **24h filter** | ⚠️ Via search params |
| **LinkedIn posts?** | ✅ `search_posts`, reactions, messages |

**Notes:** No browser — direct HTTP to LinkedIn Voyager. ⚠️ **ToS risk** — account can get restricted. Has `search_jobs()` method. Fork `4erf/linkedin2` tries to bypass the 1000-job Voyager limit with multiple accounts.

---

### 6. linkedin-api-no-cookie — P3

| | |
|---|---|
| **PyPI** | https://pypi.org/project/linkedin-api-no-cookie/ |
| **Type** | OSS (Python, fork of tomquirk) |
| **Auth** | LinkedIn credentials, no cookie file needed |

**Notes:** Variant that avoids cookie persistence issues. Same ToS concerns as #5.

---

## Category C — LinkedIn hiring *posts* & hashtag scrapers

These target informal job posts ("We're hiring!", `#SDE`, `#hiring`, "DM me") — a separate channel from formal LinkedIn Jobs listings.

### 7. Apify — LinkedIn Hiring Posts Scraper — P1

| | |
|---|---|
| **URL** | https://apify.com/apt_marble/linkedin-hiring-posts-scraper |
| **Type** | Managed (Apify Actor) |
| **Auth** | Apify API token |
| **Posts?** | ✅ Built for hiring intent phrases |
| **24h filter** | ⚠️ Implicit via recency of posts |

**Input examples:** `hiringPhrases: ["we are hiring", "now hiring"]`, `jobRoles: ["Software Engineer"]`, `locations: ["United States"]`

**Output:** Recruiter name, company, role, post URL, hiring-intent score. No login required.

---

### 8. Apify — LinkedIn Keyword Posts Monitor — P1

| | |
|---|---|
| **URL** | https://apify.com/coregent/linkedin-keyword-posts-monitor |
| **Type** | Managed (Apify Actor) |
| **Auth** | Apify API token |
| **Posts?** | ✅ Keywords + hashtags (`#fintech`, `#hiring`) |
| **24h filter** | ✅ `dateFilter: "pastMonth"` (granularity to past day varies) |

**Notes:** Discovers posts via Google `site:linkedin.com/posts` search, then fetches public post pages. No LinkedIn login. Good for hashtag monitoring.

---

### 9. Apify — LinkedIn Post Scraper (generic) — P2

| | |
|---|---|
| **URL** | https://apify.com/scrapier/linkedin-post-scraper |
| **Alt** | https://apify.com/scrapio/linkedin-post-scraper |
| **Type** | Managed |
| **Posts?** | ✅ Profiles, companies, hashtags |

**Notes:** General-purpose post scraper. We'd filter for hiring keywords ourselves.

---

## Category D — Apify LinkedIn *job listing* actors (Managed)

Managed infrastructure handles proxies, anti-bot, and scaling. Pay-per-result.

### 10. labrat-0/linkedin-jobs-scraper — P0

| | |
|---|---|
| **URL** | https://apify.com/labrat011/linkedin-jobs-scraper |
| **GitHub** | https://github.com/labrat-0/linkedin-jobs-scraper |
| **Type** | Managed (HTTP-only, no browser) |
| **Auth** | Apify token |
| **24h filter** | ✅ Via search params |
| **MCP-ready** | ✅ Works as AI agent tool via Apify MCP |

**Notes:** Pure HTTP, no login/cookies. Batch keyword × location searches. Skills extraction, recruiter info, dedup. Residential proxy recommended.

---

### 11. curious_coder/linkedin-jobs-scraper — P1

| | |
|---|---|
| **URL** | https://apify.com/curious_coder/linkedin-jobs-scraper |
| **Type** | Managed |
| **Auth** | Apify token |
| **Users** | 100k+ total runs |

**Notes:** Paste a LinkedIn Jobs search URL (from incognito with filters applied). Public version has limited filters; advanced version needs cookies.

---

### 12. curious_coder/linkedin-jobs-search-scraper (Advanced) — P2

| | |
|---|---|
| **URL** | https://apify.com/curious_coder/linkedin-jobs-search-scraper |
| **Type** | Managed |
| **Auth** | Apify token + LinkedIn cookies for advanced filters |

**Notes:** Boolean search, skills required, recruiter details. >98% success rate claimed. Needs login for full feature set.

---

### 13. bebity/linkedin-jobs-scraper — P1

| | |
|---|---|
| **URL** | https://apify.com/bebity/linkedin-jobs-scraper |
| **Type** | Managed |
| **Auth** | Apify token |

**Notes:** Simple input: job title + location + row count. 33k+ users. Good for quick smoke tests.

---

### 14. orgupdate/linkedin-jobs-scraper — P2

| | |
|---|---|
| **URL** | https://apify.com/orgupdate/linkedin-jobs-scraper |
| **GitHub** | https://github.com/orgupdate/Apify-Linkedin-Jobs-Scraper |
| **Type** | Managed |

**Notes:** Filter by posting date ("Today", "3 days"). Also aggregates via Google Jobs in some modes.

---

### 15. scrapier/linkedin-jobs-scraper — P3

| | |
|---|---|
| **URL** | https://apify.com/scrapier/linkedin-jobs-scraper |
| **Type** | Managed |

---

## Category E — Job aggregator APIs (non-LinkedIn scraping)

These are **official or licensed APIs** — more reliable than scraping LinkedIn directly. Often include LinkedIn listings indirectly via Google for Jobs.

### 16. JSearch (OpenWeb Ninja via RapidAPI) — P0

| | |
|---|---|
| **URL** | https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch |
| **Docs** | https://www.openwebninja.com/api/jsearch |
| **Type** | API (paid, free tier on RapidAPI) |
| **Auth** | RapidAPI key |
| **Sources** | Google for Jobs → LinkedIn, Indeed, Glassdoor, ZipRecruiter, Monster, etc. |
| **24h filter** | ✅ `date_posted` param |

```bash
curl --request GET \
  --url 'https://jsearch.p.rapidapi.com/search?query=software+engineer&date_posted=24h&num_pages=5' \
  --header 'x-rapidapi-host: jsearch.p.rapidapi.com' \
  --header 'x-rapidapi-key: YOUR_KEY'
```

**Notes:** 40+ fields per job including apply link, salary, skills. Best "buy vs build" option if scraping fails.

---

### 17. Adzuna API — P1

| | |
|---|---|
| **URL** | https://developer.adzuna.com |
| **Docs** | https://developer.adzuna.com/docs/search |
| **Type** | API (free tier) |
| **Auth** | `app_id` + `app_key` |
| **24h filter** | ⚠️ `max_days_old` param available |
| **Coverage** | US, UK, AU, DE, FR, IN, and more |

**Free tier limits:** 25 req/min, 250 req/day, 2,500/month.

**Helper repo:** https://github.com/shriram264/adzuna-job-scraper (Python CLI wrapper)

---

### 18. The Muse API — P2

| | |
|---|---|
| **URL** | https://www.themuse.com/developers/api/v2 |
| **Endpoint** | `GET https://www.themuse.com/api/public/jobs` |
| **Type** | API (free, no auth) |
| **24h filter** | ❌ No date filter; sort by recency |
| **Coverage** | Curated US jobs, 500k+ listings |

---

## Category F — Free public job board APIs (remote-focused)

Lower LinkedIn overlap, but zero scraping risk and no auth. Good as **supplementary sources** to hit the 100–200 job volume bar.

### 19. Remotive — P1

| | |
|---|---|
| **URL** | https://remotive.com/api/remote-jobs |
| **GitHub** | https://github.com/remotive-com/remote-jobs-api |
| **Type** | API (free) |
| **Auth** | None (max 2 req/min) |
| **24h filter** | ✅ Filter by `pubDate` client-side |
| **Coverage** | Remote jobs only |

---

### 20. RemoteOK — P1

| | |
|---|---|
| **URL** | `GET https://remoteok.com/api` |
| **Type** | API (free, no auth) |
| **Auth** | None |
| **24h filter** | ✅ Filter by date client-side |
| **Coverage** | Remote-only, 30k+ listings |

**Notes:** First JSON element is metadata; rest are jobs. Tag filter: `?tags=python,engineer`.

---

### 21. Arbeitnow — P2

| | |
|---|---|
| **URL** | `GET https://arbeitnow.com/api/job-board-api` |
| **Docs** | https://documenter.getpostman.com/view/18545278/UVJbJdKh |
| **Type** | API (free) |
| **Auth** | None |
| **Coverage** | Europe + remote |

---

### 22. Jobicy — P2

| | |
|---|---|
| **URL** | `GET https://jobicy.com/api/v2/remote-jobs` |
| **GitHub** | https://github.com/Jobicy/remote-jobs-api |
| **Type** | API (free) |
| **Auth** | None |
| **Params** | `count`, `geo`, `industry`, `tag` |
| **Coverage** | Remote, max 50 per call |

---

### 23. USAJOBS (US government) — P3

| | |
|---|---|
| **URL** | https://developer.usajobs.gov |
| **Type** | API (free, registration required) |
| **Auth** | API key + User-Agent |
| **Coverage** | US federal jobs only |

**Notes:** Niche but very reliable. Probably not primary for SWE hackathon demo unless user wants gov roles.

---

## Category G — DIY / browser automation patterns

Reference implementations if we need to build our own scraper.

### 24. Playwright + playwright-stealth (DIY) — P3

| | |
|---|---|
| **Reference** | https://dev.to/zyvop/linkedin-scraping-with-python-profiles-jobs-company-pages-1808 |
| **Type** | DIY pattern |
| **Auth** | LinkedIn session / cookies |
| **Libraries** | `playwright`, `playwright-stealth` |

**Notes:** Full control but highest maintenance. LinkedIn DOM changes break selectors frequently.

---

### 25. SuperMCP / LinkedIn MCP server — P3

| | |
|---|---|
| **Reference** | https://dev.to/developerbishwas/i-built-a-linkedin-mcp-server-for-claude-in-a-weekend-heres-the-python-playwright-pattern-59b5 |
| **Type** | MCP server (Python + Playwright) |
| **Auth** | Persistent browser storage state |

**Notes:** Interesting for Cursor integration but not ideal as Anna Executa backend.

---

## Category H — SaaS / paid scraping APIs (fallback)

Use if OSS + free APIs can't hit volume/reliability targets.

| # | Name | URL | Notes |
|---|------|-----|-------|
| 26 | **Vayne** | https://www.vayne.io | Cloud SaaS, Sales Navigator focus, low account risk |
| 27 | **Bright Data** | https://brightdata.com/products/web-scraper/linkedin | Enterprise proxy + scraper infrastructure |
| 28 | **Phantombuster** | https://phantombuster.com | Cookie hand-off cloud automation, $69+/mo |
| 29 | **ScrapingBee / ScraperAPI** | https://www.scrapingbee.com | Generic proxy + JS rendering, bring your own parser |

---

## Recommended experiment order

Based on our goals (100–200 jobs / 24h, Python Executa, hackathon timeline):

| Phase | Tools to test | Rationale |
|-------|---------------|-----------|
| **Phase 1 — Quick wins** | JobSpy (#1), JSearch (#16), Remotive + RemoteOK (#19–20) | One pip install + two free API calls. Likely hits volume bar without LinkedIn scraping pain |
| **Phase 2 — LinkedIn listings** | labrat Apify (#10), bebity Apify (#13), open-linkedin-jobs (#4) | Focused LinkedIn job data with date filters |
| **Phase 3 — LinkedIn posts** | Hiring Posts Scraper (#7), Keyword Posts Monitor (#8) | Capture informal `#hiring` / DM posts |
| **Phase 4 — Deep LinkedIn** | joeyism/linkedin_scraper (#3), tomquirk/linkedin-api (#5) | Only if Phase 1–3 fall short; higher ban risk |
| **Phase 5 — Fallback** | Adzuna (#17), curious_coder advanced (#12), SaaS (#26–29) | Paid/licensed options for production |

---

## Experiment tracking

Create `EXPERIMENT_LOG.md` entries as we test each tool:

```markdown
## Experiment: JobSpy — 2026-06-18

**Query:** software engineer, United States, hours_old=24
**Result count:** ___
**Unique in 24h:** ___
**Blocked/rate-limited?** Y/N
**Apply URL present?** __%
**Email/DM contact found?** __%
**Runtime:** ___s
**Verdict:** PASS / FAIL / PARTIAL
**Notes:**
```

---

## Key risks & constraints

| Risk | Mitigation |
|------|------------|
| LinkedIn account ban | Prefer no-login scrapers (Apify HTTP actors, JobSpy without login) or APIs (JSearch) |
| Rate limiting (~10 pages/IP on LinkedIn) | Proxies, rotate IPs, or use managed Apify actors |
| CAPTCHA | Avoid browser automation where possible; use API aggregators |
| ToS / legal | This is a personal job *suggestion* tool, not a commercial data product. Prefer licensed APIs for production. |
| Volume vs relevance | Cast wide net (200 jobs), then filter in Profile Executa (Step 2) |

---

## Next step

**Step 1b:** Pick Phase 1 tools and run local smoke tests. Record results in `EXPERIMENT_LOG.md`.

Suggested first command:

```bash
pip install -U python-jobspy pandas
python scraper-experiments/scripts/smoke_jobspy.py
```

(We will create the smoke test script in the next iteration.)
