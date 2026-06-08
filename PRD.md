# PRD — @soberadventuring Automated Content System

**Owner:** Alexis Antonelli (@soberadventuring)
**Goal:** Build a 6-figure income from Instagram by automating weekly content planning and scripting at the quality level of Lexi's top-performing posts.

---

## Problem

Manually researching trends, planning content, and scripting carousels every week takes 4-8 hours. The output quality is inconsistent. High-performing post formats don't get replicated systematically. The agent must produce content that sounds exactly like Lexi — not like an AI assistant trying to sound like Lexi.

---

## Solution

Two automated agents that run every Monday:

1. **Calendar Agent** — plans what to post across Instagram, TikTok, and Blog for the next 2 weeks
2. **Content Agent** — scripts the Instagram content that was just planned, using real engagement data and the actual slide text from top-performing posts as the quality baseline

---

## Users

**Primary:** Alexis Antonelli — reviews and approves content each Monday, then shoots/designs the actual posts

**The content persona:** Lexi Morgan (@soberadventuring) — 27, LGBTQ+, self-employed, Chiang Mai Thailand, 2 years sober. Raw autobiographer + sober freelance consultant. Building 6-figure income in public.

---

## Agent 1: Content Calendar

**File:** `generate_calendar.py`
**Trigger:** Monday 1:00am UTC (GitHub Actions cron)
**Runtime:** ~2 minutes

### What it does
- Generates 7 content entries per week for 2 upcoming weeks
- Platform mix: 3 Instagram posts (Tue–Thu), 2 TikTok (Thu–Sat), 1 Blog (Mon), 1 Building In Public (any day)
- Writes each entry as a Notion database row with: title, platform, date, content type, pillar, feeds offer, target keyword, draft caption/concept

### Mandatory distribution per week
- At least 1 Failure Archive ("By age X" structure, real numbers)
- At least 1 Contrarian Recovery Take
- At least 1 Sobriety as Entrepreneurship crossover
- 1 Building In Public update (documenting building 6 figures from Instagram)
- Blog post must soft-funnel toward ALIVE Method or PIVOT Method

### Output
Notion content calendar database (ID: `379b8973-a3ad-81f6-8b6d-d65cc244a852`)

---

## Agent 2: Content Agent

**Directory:** `content-agent/`
**Trigger:** Monday 3:00am UTC (GitHub Actions cron — 2 hours after calendar)
**Runtime:** ~15-25 minutes (Apify scrape takes the longest)

### What it does

**Step 1 — Research**
Scrapes via Apify actor `nH2AHrwxeTRJoN5hX`:
- @soberadventuring own account (50 posts) — identifies top performers by likes
- 6 hashtags (soberlife, sobriety, sobercurious, soberentrepreneur, recoveryispossible, freelancelife)
- @sobergirlsociety and @thisnakedmind competitor accounts
Falls back to `fallback_hooks.json` (real verified data) if Apify fails.

**Step 2 — Calendar read**
Queries Notion database for Instagram entries dated next week.
If found: scripts exactly those topics.
If not found: generates 6 original carousel concepts using mandatory distribution.

**Step 3 — Content generation**
Calls Claude (claude-sonnet-4-6) with:
- Full Lexi brief (character, business, voice, writing rules)
- Gold vault (actual slide text from 3 top-performing posts)
- Calendar topics from Notion
- Own top posts from Apify (what's working right now)
- Niche trend data from Apify

Generates:
- Full carousel scripts (Format A or B, matching gold vault structure)
- 4 reel concepts (6-9 second format)
- Monthly long-form piece (first Monday of month only)

**Step 4 — Output**
Priority chain:
1. Notion page (formatted with headings, callout blocks, dividers)
2. Google Doc (via service account) — if Notion fails
3. Local .md file — if both fail

**Step 5 — Email**
Summary email to `alexis.m.antonelli@gmail.com` via Gmail SMTP with output link and content count.

---

## Content Requirements

### The gold standard
Every carousel must be benchmarked against the gold vault posts:
- 775 likes: "5 reasons I partake in nightlife (alone) in sobriety"
- 214 likes: "4 (intense) childhood behaviors that predicted my future addiction"
- 123 likes: "5 scariest moments in my weed induced psychosis"

### Format A — Memoir Chapters
Use for: heavy personal history, clinical/educational + personal combo
- Cover: childhood photo OR raw unguarded Lexi face + numbered title
- Slides: named chapter header (2-5 words) + specific body text + photo direction
- Close: compassion or warm non-judgmental close

### Format B — Contrarian Reasons
Use for: Lexi does something counterintuitive in sobriety and has specific reasons
- Cover: current Lexi selfie + "N reasons I [contrarian thing]"
- Slides: reason as header + personal evidence
- Close: "Check intentions always" — non-judgmental, protects people for whom it won't work

### Voice rules (non-negotiable)
- Caption opens with specific fact or statement. Never a question. Never an emotion.
- Specific absurd detail per slide that only Lexi could give
- Self-deprecating humor that stops content being trauma porn
- "IF and only if" qualifier on anything that requires caveats
- If a piece could have been posted by any sober creator, reject and rewrite

---

## Business Logic

### The funnel
Content → followers → trust → Common Ground community → coaching calls → clients

| Pillar | Feeds |
|--------|-------|
| Failure Archive | ALIVE Method (sobriety coaching) |
| Sobriety as Entrepreneurship | PIVOT Method (freelance coaching) |
| Contrarian Recovery Takes | ALIVE Method, comment debate, shares |
| Connection as Medicine | Common Ground community |
| Life Design in SE Asia | PIVOT Method |

### Coaching offers
- **ALIVE Method** — $395/month, sobriety coaching, 3-month, free 20-min clarity call
- **PIVOT Method** — $997 flat, career/freelance coaching, 2-month, free 20-min clarity call

### Lead magnets (mentioned naturally, never with hard sell)
- "25 Things Nobody Tells You About Getting Sober"
- "What Stage of Recovery Are You In?" quiz at soberadventuring.com

---

## Hard Constraints

| Constraint | Rule |
|-----------|------|
| Kit API key | Lead capture subscribers ONLY — never for automated broadcasts |
| Writing banned structures | See CLAUDE.md — enforced in all prompts |
| Apify actor ID | `nH2AHrwxeTRJoN5hX` only — do not change |
| Workflow timing | Calendar must run before content agent — never flip the order |
| Gold vault | Must be loaded in carousel system prompt — never remove the import |

---

## Success Criteria

- Weekly: 6 carousel scripts + 4 reel concepts in Notion by Monday morning Chiang Mai time
- Quality: Every carousel has a named format (A or B), per-slide chapter headers, specific personal details, photo directions
- Relevance: Calendar topics appear in the content agent output — not generic topics
- Voice: No banned structures, no generic wellness language, no content that could have been written by any sober creator

---

## Failure Modes and Fallbacks

| Failure | Fallback |
|---------|---------|
| Apify scrape fails | `fallback_hooks.json` (real verified data) |
| Notion read fails | Content agent generates 6 original concepts (freeform mode) |
| Notion write fails | Google Docs via service account |
| Google Docs fails | Local `.md` file saved in `content-agent/` |
| Email fails | Logged to `errors.log` — output still saved |

---

## Future Scope (not built yet)

- Stories scripts — nurture layer for existing followers
- Instagram-to-Notion automation — when a post is published, log it with final performance data
- Auto-update gold vault — when a post exceeds X likes, prompt Alexis to add slide content
- TikTok scripts wired from calendar (currently reels are independent of calendar)
