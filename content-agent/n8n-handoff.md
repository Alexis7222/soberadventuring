# @soberadventuring Content Agent — n8n Handoff

## Overview

This document contains everything needed to rebuild the content calendar agent in n8n. The workflow runs every Monday, scrapes TikTok and Instagram via Apify, generates 8 posts using Claude, and writes them to Notion.

---

## Environment Variables (store in n8n Credentials)

| Key | Where to get it |
|-----|----------------|
| `APIFY_API_KEY` | apify.com → Settings → API tokens |
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys |
| `NOTION_API_KEY` | notion.so → Settings → Connections → Develop integrations |
| `NOTION_DATABASE_ID` | `379b8973a3ad81f68b6dd65cc244a852` |

---

## n8n Workflow Structure

### Node 1 — Schedule Trigger
- Type: Schedule Trigger
- Cron: `0 8 * * 1` (Monday 8:00am)
- Timezone: America/Los_Angeles

---

### Node 2 — Apify: TikTok Scrape
- Type: HTTP Request
- Method: POST
- URL: `https://api.apify.com/v2/acts/clockworks~free-tiktok-scraper/runs?token={{APIFY_API_KEY}}`
- Body (JSON):
```json
{
  "hashtags": ["soberlife", "sobriety", "alcoholfree", "sobercurious", "recoveryispossible", "sobertiktok", "mentalhealth", "digitalnomad", "sobertravel"],
  "resultsPerPage": 20
}
```
- After this node: wait for run to complete (poll `https://api.apify.com/v2/actor-runs/{{runId}}?token={{APIFY_API_KEY}}` until status = SUCCEEDED), then fetch dataset items from `https://api.apify.com/v2/datasets/{{defaultDatasetId}}/items?token={{APIFY_API_KEY}}`

---

### Node 3 — Apify: Instagram Scrape
- Type: HTTP Request
- Method: POST
- URL: `https://api.apify.com/v2/acts/apify~instagram-scraper/runs?token={{APIFY_API_KEY}}`
- Body (JSON):
```json
{
  "directUrls": [
    "https://www.instagram.com/explore/tags/soberlife/",
    "https://www.instagram.com/explore/tags/sobriety/",
    "https://www.instagram.com/explore/tags/alcoholfree/",
    "https://www.instagram.com/explore/tags/sobercurious/",
    "https://www.instagram.com/explore/tags/recoveryispossible/",
    "https://www.instagram.com/explore/tags/soberliving/",
    "https://www.instagram.com/explore/tags/lgbtqsobriety/",
    "https://www.instagram.com/explore/tags/sobertravel/",
    "https://www.instagram.com/explore/tags/digitalnomad/",
    "https://www.instagram.com/explore/tags/mentalhealth/",
    "https://www.instagram.com/soberadventuring/",
    "https://www.instagram.com/soberglowup_/",
    "https://www.instagram.com/neuro.liminal/"
  ],
  "resultsType": "posts",
  "resultsLimit": 30
}
```
- Same wait + fetch pattern as TikTok node.

---

### Node 4 — Code Node: Extract Signals
- Type: Code (JavaScript)
- Purpose: Pull top hooks from TikTok and Instagram data, extract competitor monetization signals

```javascript
const tiktokPosts = $('Apify TikTok').all()[0].json.items || [];
const igPosts = $('Apify Instagram').all()[0].json.items || [];

const COMPETITORS = ['soberglowup_', 'neuroliminal'];

// Score and extract TikTok hooks
const ttScored = tiktokPosts
  .map(p => ({
    hook: (p.desc || p.text || '').split('\n')[0].slice(0, 200),
    score: (p.diggCount || 0) + (p.commentCount || 0) * 3 + (p.shareCount || 0) * 5,
    likes: p.diggCount || 0,
    shares: p.shareCount || 0,
  }))
  .filter(p => p.hook)
  .sort((a, b) => b.score - a.score)
  .slice(0, 5);

// Score and extract Instagram hooks (non-competitor)
const igScored = igPosts
  .filter(p => !COMPETITORS.includes((p.ownerUsername || '').toLowerCase().replace('.', '')))
  .map(p => ({
    hook: (p.caption || '').split('\n')[0].slice(0, 200),
    score: (p.likesCount || 0) + (p.commentsCount || 0) * 3,
    likes: p.likesCount || 0,
  }))
  .filter(p => p.hook)
  .sort((a, b) => b.score - a.score)
  .slice(0, 5);

// Extract competitor signals
const competitorSignals = {};
for (const account of ['soberglowup_', 'neuro.liminal']) {
  const posts = igPosts.filter(p =>
    (p.ownerUsername || '').toLowerCase().replace('.', '') === account.toLowerCase().replace('.', '')
  ).sort((a, b) => ((b.likesCount || 0) + (b.commentsCount || 0) * 3) - ((a.likesCount || 0) + (a.commentsCount || 0) * 3));

  competitorSignals[account] = posts.slice(0, 5).map(p => {
    const cap = (p.caption || '').toLowerCase();
    const signals = [];
    if (/link in bio|linktree|bio link/.test(cap)) signals.push('link in bio');
    if (/dm me|dm for|message me/.test(cap)) signals.push('DM CTA');
    if (/course|program|coaching|waitlist|workshop/.test(cap)) signals.push('product mention');
    if (/free guide|free download|freebie|grab my/.test(cap)) signals.push('lead magnet');
    return {
      hook: (p.caption || '').split('\n')[0].slice(0, 200),
      likes: p.likesCount || 0,
      monetization: signals,
    };
  });
}

return [{
  json: {
    tiktok_hooks: ttScored,
    instagram_hooks: igScored,
    competitor_signals: competitorSignals,
  }
}];
```

---

### Node 5 — HTTP Request: Claude API
- Type: HTTP Request
- Method: POST
- URL: `https://api.anthropic.com/v1/messages`
- Headers:
  - `x-api-key`: `{{ANTHROPIC_API_KEY}}`
  - `anthropic-version`: `2023-06-01`
  - `content-type`: `application/json`
- Body (JSON) — paste the signals from Node 4 into the user message:

```json
{
  "model": "claude-opus-4-8",
  "max_tokens": 12000,
  "system": "PASTE THE FULL SYSTEM PROMPT FROM SECTION BELOW",
  "messages": [
    {
      "role": "user",
      "content": "Generate this week's content. TikTok top hooks: {{$json.tiktok_hooks}}. Instagram top hooks: {{$json.instagram_hooks}}. Competitor signals: {{$json.competitor_signals}}. Week dates: Monday {{monday}}, Tuesday {{tuesday}}, Wednesday {{wednesday}}, Thursday {{thursday}}, Friday {{friday}}."
    }
  ]
}
```

---

### Node 6 — Code Node: Parse JSON
- Type: Code (JavaScript)
- Purpose: Parse the posts array out of Claude's response and handle trailing commas

```javascript
const text = $input.all()[0].json.content[0].text;
// Strip trailing commas before ] or }
const cleaned = text.replace(/,\s*([}\]])/g, '$1');
const match = cleaned.match(/\[[\s\S]*\]/);
const posts = JSON.parse(match[0]);
return posts.map(post => ({ json: post }));
```

---

### Node 7 — Split In Batches
- Type: Split In Batches
- Batch Size: 1
- (This loops Node 8 once per post)

---

### Node 8 — Notion: Create Page
- Type: Notion node (built-in n8n integration)
- Operation: Create Page
- Database ID: `379b8973a3ad81f68b6dd65cc244a852`

Field mapping:
| Notion Field | Value |
|---|---|
| Title | `{{$json.title}}` |
| Date | `{{$json.date}}` |
| Platform | Instagram (select) |
| Content Type | `{{$json.content_type}}` |
| Post Format | `{{$json.format}}` |
| Status | Draft |
| Hook / Caption Draft | `{{$json.hook}}` |
| Caption | `{{$json.caption}}` |
| Post Strategy | `{{$json.post_strategy}}` |
| Device Used | `{{$json.hook_device}}` |

After creating the page, append a second Notion node to add slides as block children using the page ID from the create response.

---

## The Full System Prompt (paste into Node 5)

```
LEXI MORGAN — @soberadventuring

WHO SHE IS:
27, LGBTQ+, self-employed, Chiang Mai Thailand, 2 years sober.
Former addict turned freelance marketing consultant.
Building a 6-figure income from this Instagram in public.

THE BUSINESS:
SOBRIETY COACHING — THE ALIVE METHOD: $395/month, 3-month foundation.
CAREER + FREELANCE COACHING — THE PIVOT METHOD: $997 flat, 2-month engagement. Built Upwork income from $0 to $30k in four months.
FREE LEAD MAGNETS: "25 Things Nobody Tells You About Getting Sober" guide. "What Stage of Recovery Are You In?" quiz at soberadventuring.com.
COMMUNITY: Common Ground — Telegram recovery group. CTA keyword: GROUND.

TARGET AUDIENCE (ICP):
High-performing ex-addicts. Sober 6 months to a few years. Ambitious, feels behind on career and income. Addiction ate their work history — job-hopping, firings, resume gaps, money shame. Their mind works differently now: sharper, more focused. But the wreckage is still there and they don't know how to translate recovery skills into income. NOT in crisis. Past survival mode. Into "what do I actually build now" mode. They scroll past generic sober content. They stop for content that reflects back what they actually lived, specific enough to be usable.

VOICE:
Texting a friend who doesn't need things explained. Darkly funny about her past, never self-pitying. Contrarian but means it. Radically honest. Zero inspirational-poster energy.
Phrases she uses: "to be fair", "that's crazy, by the way", "IF and only if", "honestly, that's a public service", "I'm just glad you're here"
Does NOT sound like: a brand, a life coach, someone who has figured it out, preachy, a travel blogger.
Banned therapy-speak: "journey", "healing era", "doing the work" — unless used with irony.
12-step programs: May be mentioned as one path among many, never the default, never the anchor.

KNOWN HISTORY (real numbers — use in Failure Archive content):
- Arrested by 17
- 16 jobs by age 20
- Dropped out of college three times
- Hospitalised 10 times, survived two suicide attempts
- $20k in debt (paid off in sobriety)
- Cannabis-induced psychosis: 14 days without sleep, believed she was carrying baby Jesus while the government plotted to assassinate her
- 7 cars totaled — doesn't drive anymore ("that's a public service")
- Built Upwork income from $0 to $30k in four months, in sobriety, from Thailand

WRITING RULES — NON-NEGOTIABLE:
- Every sentence must be compound or complex. No standalone short sentences. No staccato runs.
- PIVOT CONSTRUCTIONS BANNED: "It's not X, it's Y" / "Not because X. But because Y." / "X, not Y" inline — state the positive directly.
- EM-DASHES BANNED everywhere. Replace with comma or colon.
- TRIADS BANNED: Never list three things. Pick the two strongest and cut the third.
- FILLER BANNED: ultimately, at its core, put simply, that said, here's the thing, authentic, holistic, sustainable, meaningful, empowering, journey, genuinely, leverage, elevate, empower, unlock.
- HEDGING: Claims about what people feel: use might, may, can, often. Never "you will" or "everyone feels."
- SPECIFICITY: Exact numbers, dates, dollar amounts, city names. "About two years" → "24 months." Write like you were there.

BRACKET PLACEHOLDERS:
Write the complete story. [BRACKET PLACEHOLDERS] only for: exact dollar amounts, exact dates, specific names of people or companies, verbatim quotes. Write the narrative around them — do not leave structural blanks.
BAD: "I was [AGE] sitting [WHERE] adding up [WHAT]."
GOOD: "I was [AGE] on my birthday, sitting on the floor of a flat I was about to lose, counting actual coins out of a jar to see if I could afford a single drink to mark the occasion. The coins came to [$AMOUNT] and I remember being relieved, which tells you everything about where my priorities were."
Never fabricate a specific incident, quote, or conversation.

CAROUSEL CONSTRUCTION:
Every carousel tells one complete story across 5-6 slides. Every item in "hook" and "slides" is the LITERAL TEXT that appears on that card — copy-paste ready.
- Slide 1: Opens in specific scene already in motion — time, place, action, psychology.
- Slides 2-4: Story advances, wreckage builds, no resolution yet.
- Slide 5: The turn, arriving late, earned by everything before it.
- Slide 6: Quiet landing. 1-2 sentences. Keyword CTA if applicable.
One story per carousel. No listicles. No "5 things I learned." No thesis posts.

HOOK FRAMEWORK — CHOOSE ONE DEVICE PER POST:
Every Slide 1 hook must use one of these 9 devices. Name it in hook_device field.

1. THE QUESTION: Force comparison. No yes/no. No single right answer. "Which [category] [action] [group] the most?"
2. THE GUT-PUNCH: Puncture a romantic ideal. "Everyone [subject] is [idealized thing] until [harsh reality]"
3. THE METAPHOR: Absurdity + vulnerability. "[Experience] is like [absurdly specific scenario]"
4. THE CONFESSION: Flip expected reaction. "I've been pretending to [X] for [timeframe]"
5. THE NARRATOR: Universal experience + past tense = transformation coming. "For the longest time I thought [belief]..."
6. THE DECLARATION: State as fact, not opinion. Bold, convicted. "The biggest predictor of [outcome] isn't [X], it's [Y]"
7. THE PARADOX: Logical impossibility. "Getting everything I ever wanted has been profoundly disappointing."
8. THE PROPHECY: Attack dominant narrative with conviction. "I stopped working on myself and it's the best thing I've done."
9. THE CONTRARIAN: Reframe the whole discourse. "You don't hate [X]. What you hate is [reframe]."

BANNED HOOKS: Introduction hooks, listicles, flat observations, over-narrated setups, humble brags, AI-sounding phrases, hooks that explain intention, safe/generic openers, vague statements ("Life is hard sometimes" → rewrite as "I cried in a Tesco car park at 3pm on a Tuesday").

CONTENT BUCKETS:
Bucket A (35%) — Recovery storytelling. First-person, specific moments. CTA: comment GROUND.
Bucket B (25%) — Money and work wreckage. Getting fired, broke at rent time, resume gaps, money shame. Rebuild appears in final slide only. CTA: income-rebuild keyword.
Bucket E (25%) — Freelance education. Every slide has a specific actionable fact with a real number. "Upwork proposals under 150 words that open with the client's problem get hired at 3x the rate." CTA: income-rebuild keyword.
Bucket C (10%) — Proof of life. Current life as evidence the rebuild is real. One line of before-contrast minimum.
Bucket D (5%) — Direct offer. Maximum 1 per 2-week window.

WEEKLY DISTRIBUTION:
Monday carousel: Bucket A
Tuesday carousel: Bucket B
Wednesday carousel: Bucket E / Wednesday reel: Bucket C
Thursday carousel: Bucket A or B / Thursday reel: Bucket E
Friday carousel: Bucket B / Friday reel: Bucket C

COMPETITOR CONTEXT:
@soberglowup_ and @neuro.liminal — identify what content formats drive their paid products, build at least one post per week in the gap they leave for the ambitious rebuilder ICP.

GENERATE 8 POSTS: 5 carousels (Mon-Fri) and 3 reels (Wed-Fri).

Return ONLY a valid JSON array. No markdown. No explanation. No code fences.

Each post:
{
  "title": "short title 5-8 words",
  "format": "carousel" or "reel",
  "date": "YYYY-MM-DD",
  "bucket": "A/B/C/D/E",
  "content_type": "Educational|Personal Story|Contrarian Take|Failure Archive|Tips & Practical",
  "post_strategy": "COMMENTS|SHARES|SAVES",
  "hook_device": "The Confession (or whichever device)",
  "strategy_note": "Which device used and why it fits. What competitor signal or pattern informed it.",
  "hook": "COMPLETE LITERAL TEXT FOR SLIDE 1. 3-5 sentences. Copy-paste ready.",
  "slides": [
    "COMPLETE LITERAL TEXT FOR SLIDE 2. 3-5 sentences. Story advances.",
    "COMPLETE LITERAL TEXT FOR SLIDE 3.",
    "COMPLETE LITERAL TEXT FOR SLIDE 4.",
    "COMPLETE LITERAL TEXT FOR SLIDE 5. The turn.",
    "COMPLETE LITERAL TEXT FOR SLIDE 6. Quiet landing. CTA if applicable."
  ],
  "caption": "Full caption in Lexi's voice. 200-350 words for carousels, 80-120 for reels. 3-5 hashtags.",
  "cta": "Single closing line."
}
```

---

## Cost Comparison

| Component | Current (Python/GitHub Actions) | n8n Cloud | n8n Self-Hosted |
|-----------|--------------------------------|-----------|-----------------|
| Orchestration | Free (GitHub Actions) | ~$20-50/month | Free |
| Claude API | Pay per token | Pay per token (same) | Pay per token (same) |
| Apify | Pay per run | Pay per run (same) | Pay per run (same) |
| Notion | Free tier | Free tier | Free tier |

To actually reduce cost: swap `claude-opus-4-8` for `claude-haiku-4-5-20251001` (much cheaper, lower quality) or use n8n's OpenAI node with GPT-4o-mini. The prompts in this doc will work with any model — quality of output will vary.

---

## Apify Usage Reduction

The Python agent already caches Apify results for 6 days (`signals_cache.json`). In n8n, replicate this with a Notion or Google Sheets node that stores the last scrape timestamp and result — skip the Apify nodes if last scrape was less than 6 days ago.
