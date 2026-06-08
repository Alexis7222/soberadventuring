# CLAUDE.md — @soberadventuring Content System

This file loads automatically in every Claude Code session on this repo.
Read it before touching anything.

---

## CRITICAL RULES — DO NOT VIOLATE

### index.html IS LOCKED — DO NOT TOUCH
**`index.html` must never be modified, rewritten, or replaced without the user explicitly saying "edit index.html" or "rewrite the homepage."**

This file has been rebuilt multiple times by accident. It is the production homepage. Treat it as read-only unless you have a direct, unambiguous instruction to change it. Voice passes, SEO fixes, content agent updates, blog work, and general cleanup tasks do NOT qualify as permission to touch this file.

If the user asks about the website or the homepage in general terms, do not assume that means edit `index.html`.

### Kit API Key
The Kit API key (`BaTfF2IFpZdAuoig0JYgIg`) is for **lead capture subscribers ONLY**.
It is the list of people who opted in at soberadventuring.com for the lead magnet.
**NEVER use it for internal broadcasts, automated content delivery, or agent outputs.**
If you're tempted to use Kit for anything automated, stop. Use Gmail SMTP instead.

### Writing Rules — Banned Forever
These are banned in every piece of content this system produces. No exceptions.

**Banned structures:**
- "Not because X. But because Y." — all forms
- "It's not X. It's Y." — all forms
- "isn't X, it's Y" — all forms
- Any two-sentence negative/positive pivot
- Em dashes — banned everywhere
- Fragment kickers: "Simple." / "Real talk." / "Full stop." / "Period."
- Short standalone dramatic sentences stacked for effect

**Banned words:** delve into, journey, transformative, game-changer, holistic, leverage,
pivotal, embark, unpack, dive into, at the end of the day, cutting-edge, seamlessly,
robust, comprehensive, tapestry, beacon, resonate, foster, navigate, empower, thrive

**Caption rule:** Always opens with a specific fact or statement. Never a question. Never an emotion.

---

## SYSTEM ARCHITECTURE

Two GitHub Actions workflows running in sequence every Monday:

```
Monday 1:00am UTC  →  weekly-calendar.yml  →  generate_calendar.py
Monday 3:00am UTC  →  weekly_content.yml   →  content-agent/main.py
```

The calendar plans WHAT to post. The content agent scripts HOW.
The 2-hour gap ensures the calendar always completes before the content agent reads it.

### Calendar Agent (`generate_calendar.py`)
- Generates 2 weeks of content ideas for Instagram, TikTok, Blog
- Writes each entry as a row in the Notion content calendar database
- Uses: `ANTHROPIC_API_KEY`, `NOTION_API_KEY`, `NOTION_DATABASE_ID`, `NOTION_PARENT_PAGE_ID`

### Content Agent (`content-agent/`)
- Reads this week's Instagram topics from Notion (what the calendar just planned)
- Scrapes @soberadventuring + hashtags + competitors via Apify
- Generates full carousel scripts and reel concepts
- Saves output to Notion page, falls back to Google Docs, then local .md
- Emails summary to alexis.m.antonelli@gmail.com
- Uses all secrets (see GitHub Secrets section below)

---

## KEY FILE LOCATIONS

| File | Purpose |
|------|---------|
| `content-agent/prompts/gold_vault.py` | Real slide text from top 3 performing posts — the gold standard every carousel must match |
| `content-agent/prompts/character_brief.py` | Full Lexi Morgan character brief with real Apify engagement data |
| `content-agent/prompts/carousel_prompt.py` | Carousel generation prompt — imports gold vault |
| `content-agent/prompts/reel_prompt.py` | Reel generation prompt |
| `content-agent/modules/scraper.py` | Apify scraper — uses actor `nH2AHrwxeTRJoN5hX` |
| `content-agent/modules/notion_reader.py` | Reads calendar topics from Notion before generating |
| `content-agent/modules/scripter.py` | Orchestrates Claude API calls |
| `content-agent/modules/output.py` | Notion → Google Docs → local .md output chain |
| `content-agent/modules/emailer.py` | Gmail SMTP summary email |
| `content-agent/fallback_hooks.json` | Real engagement data used when Apify fails |
| `generate_calendar.py` | Calendar agent — standalone script |

---

## CORRECT IDs AND ENDPOINTS

| Thing | Value |
|-------|-------|
| Apify actor | `nH2AHrwxeTRJoN5hX` — the ONLY one that works for @soberadventuring |
| Notion database | `379b8973-a3ad-81f6-8b6d-d65cc244a852` — stored as `NOTION_DATABASE_ID` secret |
| Claude model | `claude-sonnet-4-6` — used in both agents |
| Gmail SMTP | `smtp.gmail.com:587`, STARTTLS, app password in `GMAIL_APP_PASSWORD` secret |
| Email recipient | `alexis.m.antonelli@gmail.com` |

---

## GITHUB SECRETS (all must be set)

```
ANTHROPIC_API_KEY         — Claude API
APIFY_API_TOKEN           — Apify scraping
NOTION_API_KEY            — Notion integration token
NOTION_DATABASE_ID        — Content calendar DB: 379b8973-a3ad-81f6-8b6d-d65cc244a852
NOTION_PARENT_PAGE_ID     — Parent page for content agent output pages
GOOGLE_SERVICE_ACCOUNT_JSON — Google service account for Docs fallback
GOOGLE_DRIVE_FOLDER_ID    — Drive folder for Docs fallback
GMAIL_APP_PASSWORD        — Gmail app password for summary email
```

---

## THE GOLD VAULT

`content-agent/prompts/gold_vault.py` contains the actual slide text from Lexi's 3 top-performing carousels:

1. **775 likes** — "5 reasons I partake in nightlife (alone) in sobriety" — Format B (contrarian reasons)
2. **214 likes** — "4 (intense) childhood behaviors that predicted my future addiction" — Format A (memoir chapters)
3. **123 likes** — "5 scariest moments in my weed induced psychosis" — Format A (memoir chapters)

**Format A** = memoir chapters, clinical/experiential headers, raw archival photos, compassion close
**Format B** = contrarian reasons list, casual voice, atmospheric real-life photos, "check intentions always" close

The gold vault is imported directly into the carousel system prompt. Every generation run sees the actual slide text before writing anything. When adding new top-performing posts, add them to `GOLD_POSTS` in gold_vault.py.

---

## CONTENT IDENTITY

**Who Lexi is:** 27, LGBTQ+, self-employed, Chiang Mai Thailand, 2 years sober. Building a 6-figure income from @soberadventuring in public.

**The business:**
- ALIVE Method — sobriety coaching, $395/month, 3-month, free 20-min clarity call
- PIVOT Method — career/freelance coaching, $997 flat, 2-month, free 20-min clarity call
- Common Ground — Telegram recovery community
- Lead magnets at soberadventuring.com

**The moat:** Raw autobiographer + sober freelance consultant + LGBTQ+ + SE Asia nomad. No one else in the niche has all four.

**The rule:** If a piece of content could have been posted by any sober creator, it gets rejected. Every carousel must require Lexi's specific history, specific numbers, or specific locations.

---

## RUNNING MANUALLY

```bash
# Calendar agent
cd /path/to/repo
pip install anthropic requests
ANTHROPIC_API_KEY=... NOTION_API_KEY=... NOTION_DATABASE_ID=... python generate_calendar.py

# Content agent
cd content-agent
pip install -r requirements.txt
ANTHROPIC_API_KEY=... APIFY_API_TOKEN=... NOTION_API_KEY=... NOTION_DATABASE_ID=... python main.py
```

To trigger via GitHub: Actions tab → select workflow → Run workflow.

---

## WHAT NOT TO DO

- Do not change the Apify actor ID — `nH2AHrwxeTRJoN5hX` is the only verified working actor
- Do not use Kit API for anything automated — lead capture subscribers only
- Do not change the cron timing without understanding the calendar → content agent dependency
- Do not generate content without the gold vault loaded — it's the entire quality standard
- Do not write captions that open with a question or emotion
- Do not add em dashes anywhere
