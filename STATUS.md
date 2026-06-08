# STATUS.md — Sober Adventuring Project Management Doc

Last updated: 2026-06-08

This file is the persistent project memory for soberadventuring.com. Update it whenever a system changes, a bug is fixed, or something breaks. Read it at the start of every session.

---

## LIVE SYSTEMS

| System | Status | Notes |
|--------|--------|-------|
| GitHub Pages | LIVE | Push to `main` → deploys automatically. No build step. |
| Cloudflare Worker | LIVE | `https://bitter-star-c87e.alexis-m-antonelli.workers.dev` |
| Kit (ConvertKit) | LIVE | Lead capture subscribers only. Never use for automated content. |
| Resend | LIVE | Sends guide PDF email on guide signups |
| Google Analytics | PLACEHOLDER | Replace `G-XXXXXXXXXX` in index.html with real Measurement ID |

---

## WORKER CONFIGURATION

**Worker name:** `bitter-star-c87e`
**Worker URL:** `https://bitter-star-c87e.alexis-m-antonelli.workers.dev`
**Deploy command:** `wrangler deploy` inside `C:\Users\Alexis\sa-worker\`

### Environment Variables (set in Cloudflare dashboard)

| Variable | Value | Purpose |
|----------|-------|---------|
| `ADMIN_KEY` | `soberadventuring2026` | Password for `/alexis7222` admin dashboard GET requests |

### KV Namespace (set in Cloudflare dashboard)

| Binding | Namespace Name | Purpose |
|---------|---------------|---------|
| `LEADS` | LEADS | Stores every lead submitted through any form |

**Setup complete as of 2026-06-08.** KV namespace ID: `c40f0fc7a633497d9a62116cdbcc1e06`. ADMIN_KEY set. Worker deployed.

### API Keys (hardcoded in worker.js)

| Key | Purpose |
|-----|---------|
| `kLE8c64ibLP3V5X-OqCTsQtqrk7De9pTI-uaBVXWmlY` | Kit API secret — lead capture only |
| `re_Rp73LAWV_LV7k9SQUWkkTQ6cPPf5b4u9U` | Resend API key |

### Kit Tag IDs

| Tag | ID | Trigger |
|-----|----|---------|
| guide | 20114246 | Any guide signup (sends PDF email) |
| result-a | 20114247 | Recovery quiz result A |
| result-b | 20114248 | Recovery quiz result B |
| result-c | 20114249 | Recovery quiz result C |

---

## KEY FILES

| File | Purpose | Notes |
|------|---------|-------|
| `index.html` | Production homepage | LOCKED — never edit without explicit "edit index.html" instruction |
| `sa-worker/worker.js` | Unified Cloudflare Worker | KV storage + Kit + Resend + GET handler |
| `sa-worker/wrangler.toml` | Worker deployment config | Has KV namespace placeholder — fill in before deploying |
| `workers/leads-worker.js` | Old version (incomplete) | Superseded by sa-worker/worker.js. Keep for reference. |
| `alexis7222/index.html` | Admin leads dashboard | Fetches leads via GET from Worker |
| `quiz/index.html` | Freelance quiz | "Is Freelancing Your Next Move?" |
| `quiz/recovery/index.html` | Recovery quiz | "What Stage of Recovery Are You In?" |
| `CLAUDE.md` | Auto-loads in every session | Writing rules, system architecture, locked files |

---

## BLOG POSTS THAT EXIST

All at `/blog/<slug>/index.html`:

| Slug | Title |
|------|-------|
| `sober-life-coaching-approach` | What a Sobriety Coach Does (and Doesn't) |
| `build-sober-life-want-to-live` | How to Build a Sober Life You Actually Want to Live |
| `sober-travel-guide` | Complete Guide to Sober Travel: Tips & Strategies |
| `how-to-start-freelancing-upwork-no-experience` | How to Start Freelancing on Upwork With No Experience |

Only link to these from the homepage. Do not invent post titles.

---

## BRAND / DESIGN

**Colors:** `--ink:#1B0009` `--forest:#2D3D24` `--terra:#C5442C` `--cream:#F4E8D0` `--paper:#F0EDE8`
**Fonts:** DM Serif Display, Bricolage Grotesque, Caveat

**Community:** Common Ground = the Telegram group. The weekly meeting happens inside it. One thing, one link: `https://t.me/+wJbhwv2ccS1hMjFh`

---

## BUG HISTORY

| Date | Bug | Fix | Status |
|------|-----|-----|--------|
| 2026-06 | Site reverted to old design after GitHub Actions push | Added index.html lock rule to CLAUDE.md | Fixed |
| 2026-06 | Guide email not sending | Worker was only handling POST with no KV; unified worker created | Fixed |
| 2026-06 | Admin dashboard GET returned 405 | Old worker blocked GET; unified worker adds GET handler | Fixed (pending KV setup) |
| 2026-06 | Recovery quiz CTA linked to `/quiz/` (freelance quiz) | Changed link to `/quiz/recovery/` | Fixed |
| 2026-06 | Em dashes throughout index.html | Replaced all `&mdash;` with commas/periods | Fixed |
| 2026-06 | Community section showed two cards (same Telegram link) | Collapsed to one card explaining Telegram = group + meeting | Fixed |
| 2026-06 | Blog post links pointed to fake posts | Updated to only link real posts with correct URLs | Fixed |

---

## PENDING / TODO

- [ ] KV namespace setup (see Worker Configuration above) — required for admin dashboard to show leads
- [ ] Replace `G-XXXXXXXXXX` in index.html with real Google Analytics 4 Measurement ID
- [ ] Test full email deliverability: submit guide form → confirm Kit subscription fires → confirm Resend email arrives → confirm PDF at `https://soberadventuring.com/25-hot-takes.pdf` is accessible
- [ ] Verify both quizzes submit correctly to the Worker and leads appear in `/alexis7222`

---

## WRITING RULES (summary — full rules in CLAUDE.md)

- No em dashes anywhere
- No "Not because X. But because Y." pivot constructions
- No fragment kickers (Simple. Real talk. Full stop.)
- No short standalone dramatic sentences stacked for effect
- Lists of three are an AI tell — keep to one or two points
- Captions open with a statement or specific fact, never a question or emotion
