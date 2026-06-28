---
name: market-sweep
description: Run a job market intelligence sweep for a senior technical candidate, produce a tier-ranked report in the vault, run an automated recruiter review, improve the report in-place, and optionally set up weekly automation.
---

# Market Sweep

Produces a structured job market intelligence report for a senior technical candidate targeting remote US roles. Writes the report to a vault, runs an automated recruiter review pass, improves the report in-place, and offers to schedule weekly repeats.

**Designed for:** Staff/Director/Principal-level engineering, data, and analytics candidates targeting remote US roles at $150k+. Generalizes to other disciplines via the criteria step.

If Auto mode is not active, suggest the user enable it with `/auto` before proceeding — the skill runs several sequential research and write operations.

---

## Step 0: Load or Collect Criteria (Gate)

Check the vault for a criteria file at `<vault>/career/search-criteria.md`. If it exists, read it and display a summary — ask the user to confirm it's current or update it. If it does not exist, ask the user for:

1. **Role types** — list of target titles (e.g., "Analytics Engineering Manager, Director of Analytics, Head of Data/Analytics, Principal Analytics Engineer")
2. **Location** — default "Remote US only"
3. **Compensation floor** — default "$150,000+ base"
4. **Stack keywords** — tools to prioritize in role matching (e.g., "dbt, Snowflake, Databricks, SQL, Python")
5. **Seniority** — title-level signals (e.g., "Manager, Director, Head, Principal, Staff, Lead")
6. **Priority filter** — any company type to weight highest (e.g., "Women-led companies: CEO/Co-founder/significant exec")
7. **Domain bonus** — industries or verticals that are a bonus fit (e.g., "B2B SaaS, Healthcare/Life Sciences, Data Platforms")
8. **Exclude** — hard filters to apply (e.g., "crypto/web3, junior/intern, on-site only, security clearance")

Save confirmed criteria to `<vault>/career/search-criteria.md` for reuse in future sweeps.

---

## Step 1: Research Sweep

Using web search, research the current job market for the candidate's criteria. The report is **market intelligence**, not a job board dump. Cover:

### 1a. Market Conditions
- Current macro hiring signals for the target role level (up/down vs. prior quarter)
- Any major layoffs or hiring surges in the target domain
- Volume indicators (e.g., total active remote listings on Glassdoor for target titles)
- What the market conditions mean specifically for a candidate at this level

### 1b. Priority Companies
Research companies matching the priority filter (e.g., women-led) with confirmed active roles:
- Verify CEO/founder identity for any "women-led" claim before including
- Search each company's careers page for active openings, not just aggregator listings
- Note whether the role is confirmed Remote US or has eligibility uncertainty

### 1c. Additional Strong Matches
Search beyond the priority filter for roles meeting comp and stack criteria at well-funded, stable companies.

### 1d. Stack & Market Trends
- What tools are appearing in senior JDs right now
- Any tool shifts (rising/falling) vs. prior period
- What differentiated expertise looks like at the director/staff level

### 1e. Compensation Intelligence
- Role-level comp benchmarks for target titles (sourced from Levels.fyi, Built In, Glassdoor)
- Any comp compression or expansion signals
- Negotiation considerations (location calibration, sign-on trends, equity changes)

---

## Step 2: Write First Draft

Write a structured Markdown report to:
```
<vault>/reports/job-market-YYYY-MM-DD.md
```
Use today's date. Create the `reports/` directory if it does not exist.

**Required report structure:**

```markdown
# Job Market Intelligence Report
**Search Date:** [today]
**Prepared for:** [candidate name]
**Revision:** v1 — first draft

---
## Criteria Summary
[table of search criteria]

---
## Market Conditions ([Month Year])
[market analysis]

---
## Priority Companies Actively Hiring
[per company: CEO/leader name and verification, active role found or "no current opening", remote eligibility note, stack fit note]

---
## Curated Role List

### Tier 1: [Priority filter] + Confirmed Active + $[floor]+
[Only roles with confirmed active openings go here. Mark any with unconfirmed remote eligibility as "Conditional — verify before applying."]

### Tier 2: Strong Comp + Good Fit
[Confirmed active roles at strong companies that do not meet the priority filter]

### Tier 3: Monitor
[No confirmed role yet but high potential — set job alert, networking entry point. Include "Watch for:" entries here, NOT in Tier 1.]

### Excluded from Active List (Criteria Mismatch)
[Any role researched but excluded, with one-line reason]

---
## Company Vitals (Tier 1)
[headcount, last funding round, ATS, approx time-to-offer for each Tier 1 company]

---
## Who to Reach at Tier 1 Companies
[per company: how to identify the hiring manager or internal recruiter, warm outreach approach]

---
## Stack & Market Trends
[tech stack signals, emerging tools in JDs, differentiation opportunities]

---
## Compensation Intelligence
[role-level benchmark table, active posting data points, comp trend signals]

---
## Application Strategy
1. [Specific positioning advice for this candidate's profile]
2. [Sequenced application order with timing rationale]
3. [Networking tactics specific to the companies found]
4. [Company-specific interview process notes]
5. [Negotiation considerations]

---
## How to Run This Report Weekly
[Instructions for using /schedule to set up a weekly sweep that writes dated reports to <vault>/reports/ — reference the /schedule skill]

---
## About This Report
*Generated by /career:market-sweep — [date]. Criteria: [one-line summary].*

**Sources consulted:**
[list all URLs used]
```

**Quality gates before writing:**
- Every Tier 1 entry must have a confirmed active opening (not "Watch for:")
- Every "women-led" or priority filter claim must have the leader's name and role verified
- No role may appear in an active tier AND be excluded by a hard filter (e.g., not Remote US)
- Any claim about a named industry initiative must be verifiable — do not include unverifiable branded names

---

## Step 3: Recruiter Review

After the first draft is written, run an automated recruiter review by spawning a sub-agent with this prompt (adapt as needed):

> "You are a senior technical recruiter with 10+ years placing [target role type] talent at [target industries]. Read the job market report at `<vault>/reports/job-market-YYYY-MM-DD.md`. Review it for: (1) Tier contamination — Tier 1 entries that are unconfirmed or ineligible, (2) factual errors in company descriptions or leader verification, (3) roles that fail hard filters but slipped through, (4) missing intelligence a recruiter would always check (Glassdoor ratings, funding stage, time-to-offer, named contacts), (5) missing companies worth adding. Write your review to `<vault>/reports/recruiter-review-YYYY-MM-DD.md` using this structure: Overall Assessment, What Works, Issues to Fix (numbered), Missing Intelligence, Recommended Additions, Line-Level Edits."

Wait for the review agent to complete.

---

## Step 4: Apply Improvements

Read both the original report and the recruiter review. Apply all Issues to Fix and Recommended Additions to the original report. Mark the report as **Revision v2** in the header.

Key improvement priorities (in order):
1. Fix any Tier contamination (move unconfirmed "Watch for:" entries to Tier 3)
2. Fix any criteria-mismatch entries in active tiers (move to Excluded section)
3. Fix any factual errors in company descriptions
4. Add Company Vitals table if missing
5. Add Who to Reach section if missing
6. Add any missing companies identified in the review
7. Improve Application Strategy with sequencing and company-specific prep notes

Overwrite the original file in-place (do not create a new file). Update the revision line from v1 to v2.

---

## Step 5: Commit to Vault

```bash
git -C <vault> add reports/
git -C <vault> commit -m "feat: add job market intelligence report [date] (v2 with recruiter review)"
git -C <vault> push
```

---

## Step 6: Offer Weekly Schedule (Gate)

Present the user with the option to set up weekly automation:

> The report is complete. To run this sweep automatically every Sunday night and accumulate a time-series of market intelligence in your vault, use `/schedule` to create a weekly agent routine.
>
> **Suggested schedule:** `0 20 * * 0` (Sundays at 8pm PT)
> **Output:** `<vault>/reports/job-market-YYYY-MM-DD.md` (each week a new dated file)
> **Weekly prompt focus:** What changed vs. last week — new openings at priority companies, status changes, new women-led companies, comp signals.
>
> Run `/schedule` now to configure it, or skip and run `/career:market-sweep` manually whenever you want a fresh sweep.

---

## Idempotency

Re-running is safe:
- If `search-criteria.md` exists, it is read (not overwritten) unless the user explicitly updates it
- Report files are dated — each run creates a new file; existing reports are never overwritten
- The recruiter review file is also dated and is created fresh each run
- The git commit uses the dated filename so re-running on the same day appends nothing unexpected
