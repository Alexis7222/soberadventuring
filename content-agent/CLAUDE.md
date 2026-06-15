# @soberadventuring Content Calendar Agent

## What This Is

A Python agent that runs weekly to generate Instagram content for @soberadventuring (Lexi Morgan). It scrapes TikTok and Instagram for trending hooks via Apify, analyzes competitor monetization patterns (@soberglowup_ and @neuro.liminal), generates 8 posts per week using Claude Opus, and writes them to a Notion content calendar.

**Run it:** `python main.py --now`
**Scheduled run:** Monday 8:00am Pacific — `python main.py`

## Architecture

| File | Role |
|------|------|
| `main.py` | Entry point, orchestrates scrape → generate → save |
| `scraper.py` | Apify calls for TikTok hashtags and Instagram competitor data |
| `scripter.py` | All Claude prompts, content briefs, and JSON parsing |
| `notion_output.py` | Writes posts to the Notion database |
| `fallback_hooks.json` | Used if Apify scraping fails |
| `signals_cache.json` | Cached Apify signals — skips Apify on re-runs within 6 days |
| `signals_library.json` | Growing library of all scraped signals, up to 52 weeks |

## Environment Variables (`.env`)

```
APIFY_API_KEY=...
ANTHROPIC_API_KEY=...
NOTION_API_KEY=...
NOTION_PARENT_PAGE_ID=379b8973a3ad81f68b6dd65cc244a852   ← soberadventuring DB
```

The `NOTION_PARENT_PAGE_ID` must always be the soberadventuring database. The Alderwood ID (`37cb8973...`) must never be used here.

---

## Character Brief: Lexi Morgan (@soberadventuring)

**Identity:** 27, LGBTQ+, self-employed, Thailand-based, 2 years sober. Raw autobiographer, sober freelance marketing consultant, SE Asia nomad.

**Core angle:** The skills that keep me sober are the same skills that built my business. Same toolkit, two different outcomes.

**Voice:** Sounds like texting a friend who doesn't need things explained. Darkly funny about her past, never self-pitying. Contrarian but means it. Radically honest. Zero inspirational-poster energy. Zero life-coach energy.

**Phrases she uses:** "to be fair", "that's crazy, by the way", "IF and only if", "honestly, that's a public service", "I'm just glad you're here"

**Does NOT sound like:** a brand, a life coach, someone who has figured it out, preachy, a travel blogger, generic wellness.

**Banned therapy-speak:** "journey", "healing era", "doing the work" — unless used with irony. If it could go on a mug, cut it.

**12-step programs:** May be mentioned as one valid path among many, never as the default explanation, never as the anchor of any post. Do not use 12-step as a crutch or shorthand for sobriety.

---

## Target Audience (ICP)

Every post is written to attract and qualify this specific person: **high-performing ex-addicts.** Sober anywhere from 6 months to a few years. Ambitious, feels behind on career and income, knows it. Addiction ate their work history — the job-hopping, the firings, the resume gaps, the money shame, the identity crisis of being 27 or 32 with nothing to show for it financially. Their mind works differently now that they're sober: sharper, more focused, more disciplined than most people they know. But the wreckage is still there and they don't know how to translate the recovery skills into income.

They are NOT in crisis. They are past survival mode and into "what do I actually build now" mode. They scroll past generic sober content. They stop for content that reflects back what they actually lived and shows proof that the rebuild is possible and specific enough to be usable.

**The product they buy:** an income-rebuild guide for people in recovery, built around freelancing and Upwork. The feed attracts and pre-qualifies through story. ManyChat keyword CTAs handle conversion. The product is never named or pitched except in Bucket D posts.

---

## Content Buckets

**Bucket A — Pure recovery storytelling (35%):**
First-person, vulnerable, specific moments from addiction and early recovery. Carousel format. Story arc across slides. Attracts the ICP and builds trust through recognition. CTA: keyword GROUND ("if this is you, comment GROUND") or none.

**Bucket B — Money and work wreckage storytelling (25%):**
Same genre and tone as Bucket A. Subject matter is financial and career identity: getting fired, job number N of many, being broke at rent time, money shame, interviews while hungover, the identity hit of having no career story to tell at 30. The rebuild appears in the final 1-2 slides only as a brief hook, never as a tutorial. CTA: ManyChat keyword for the income-rebuild lead magnet.

**Bucket E — Freelance education, hyper-specific and usable (25%):**
Every slide must contain a specific, actionable fact or tactic the reader can use today. Examples: "Upwork proposals under 150 words that open with the client's specific problem get hired at 3x the rate of generic ones." Or: "Your first 3 Upwork reviews matter more than your rate — take jobs at $15/hr to build them, then raise immediately." Anchor every post in Lexi's experience with [BRACKET PLACEHOLDERS] for her real numbers. CTA: ManyChat keyword for the income-rebuild lead magnet.

**Bucket C — Documentation and proof of life (10%):**
Lexi's current life as evidence the rebuild is real. Muay Thai training, Chiang Mai daily life, client work moments. Always anchored to the BEFORE with one line of contrast.

**Bucket D — Direct offer (5%):**
Explicit posts about the Upwork guide or coaching. Maximum 1 per 2-week window. Story-wrapped.

**Weekly distribution:**
- Monday carousel: Bucket A
- Tuesday carousel: Bucket B
- Wednesday carousel: Bucket E / Wednesday reel: Bucket C
- Thursday carousel: Bucket A or B / Thursday reel: Bucket E
- Friday carousel: Bucket B / Friday reel: Bucket C

---

## Writing Rules

Apply to every word in every field: captions, slides, CTAs, hook lines.

**Sentence structure:** Every sentence must be compound or complex. Standalone short sentences are banned. No staccato runs (3+ short sentences in a row). No fragment mic-drops. No punchy standalone kickers — fold them into the preceding sentence.

**Pivot constructions — banned everywhere:**
- "It's not X, it's Y" — state the positive directly
- "Not because X. But because Y." — drop the foil
- "X, not Y" inline — banned; say the positive and stop
- "You're not stuck because X; you're stuck because Y" — reframe as direct positive

**Em-dashes — banned everywhere.** Replace with a comma, colon, or rewrite.

**Triads — hard stop.** Never list three things anywhere. Pick the two strongest and cut the third. No exceptions.

**Filler words — delete on sight:** "ultimately", "at its core", "put simply", "that said", "in other words", "here's the thing", "at the end of the day", "authentic", "holistic", "sustainable", "meaningful", "empowering", "journey", "genuinely", "leverage", "elevate", "empower", "unlock", "seamless", "robust".

**Hedging:** When making statements about what people experience or feel, use: might, may, can, often, for many people, in a lot of cases. Never "you will" or "everyone feels."

**Specificity:** Exact numbers, dates, dollar amounts, city names, percentages. "About two years" is weaker than "24 months." "A lot of money" is weaker than "$2,400 a month." Write like you were actually there.

---

## Scaffold Rules (Bracket Placeholders)

Write the complete story. The narrative arc, the sequence of events, the psychology, the pacing, the voice — all fully written. `[BRACKET PLACEHOLDERS]` are reserved ONLY for specific personal facts that cannot be known: exact dollar amounts, exact dates, exact addresses or place names, specific names of people or companies, verbatim quotes.

Think of it as: write the story, leave blanks for the numbers. A slide should have at most 1-2 brackets surrounded by fully written story content. It must read like a scene, not a template.

**BAD (too many brackets, no story):**
"It was [LEXI: the date] and rent was due, and I was sitting [LEXI: where] adding up [LEXI: what] to see if I could cover it without [LEXI: what you'd have to do]."

**GOOD (story written, only the specific fact bracketed):**
"It was the [DATE] and rent was due. The ritual was always the same: check the main account, then the savings, then the backup card I wasn't supposed to need, and add them in order from most to least humiliating. The number came out [$XX] short, which was enough to make the phone feel heavy in my hand and not enough to make me ask for help yet."

**Never fabricate specific personal incidents.** Do not invent a Muay Thai training moment, a therapist quote, a specific conversation, a specific person's name. Write the structure, leave brackets for the specifics only you can fill in.

---

## Carousel Construction

Every carousel tells one complete story across 5 slides minimum. The reader follows the narrative from slide 1 to slide 6 without needing to fill in any bracket to understand what happened.

- **Slide 1:** Opens in a specific scene already in motion — time, place, action, psychology. The ICP recognises their own life immediately.
- **Slides 2-4:** Each slide advances the story with the next specific detail. The wreckage builds. No resolution yet. The turn is not allowed to arrive early.
- **Slide 5:** The turn, earned by everything before it. Arrives late. Is felt, not announced.
- **Slide 6:** Quiet landing line. One or two sentences. Never a summary. Keyword CTA if applicable.

**Critical rule:** Every item in the `hook` and `slides` fields of the JSON output is the LITERAL TEXT that appears on that carousel card — copy-paste ready. Not a description of what to write. The actual copy. When someone opens Notion and reads slide 2, they see the exact words that go on the card.

**Good slide 1 example (Bucket B — Narrator device):**
"For the longest time I thought being broke was just my personality, the way some people are tall. I was [AGE] on my birthday, sitting on the floor of a flat I was about to lose, counting actual coins out of a jar to see if I could afford a single drink to mark the occasion. Not a meal, not a gift to myself, a drink. The coins came to [AMOUNT] and I remember being relieved, which tells you everything about where my priorities were."

**Good slide example (Bucket E):**
"Your Upwork proposal should be under 150 words and should open with the client's problem, not your name, because that's what actually gets hired. Most proposals lose in the first sentence by leading with 'Hi, I'm [name] and I have 5 years of experience' — the client is not reading past that. Open with: 'I noticed your site has [specific problem] — here's exactly how I'd fix it.' That one sentence puts you in the top 10% of applicants."

One story per carousel. No listicles. No "5 things I learned." No thesis posts.

---

## Hook Frameworks — Full Training

Every Slide 1 must consciously use one of these 9 literary devices. Name the device in `strategy_note`. A hook that could have been said by anyone will be remembered by no one.

### What NEVER Works

- **Introduction hook:** "Hi guys, so today I wanted to talk about..." — not a hook, it's a warm-up. Intros are out.
- **Listicles:** "My favorite things to do in...", "Everything I ate in...", "The best ways to..." — dead format unless the framing is wildly original.
- **Flat observations:** "Travelling is important because..." — no tension, no surprise, no emotion. Anyone could say this.
- **Over-narrated setups:** "Last year I quit my corporate job" / "I made 200k at 20 years old" — used to work until everyone started doing it. Start at the climax.
- **The humble brag:** "I never expected 100K followers..." — audiences smell inauthenticity. Flex disguised as gratitude = disengage.
- **AI-generated language:** "In a world where authenticity matters..." — if it sounds like ChatGPT wrote it, people feel it. Generic language = generic engagement.
- **Hooks that explain:** "I want to share why I think..." — don't tell people what you're about to do. Just do it. Explaining kills mystery.
- **Hooks that are too safe:** "I've been thinking about self-care lately" — safe hooks get safe engagement. Push into discomfort.
- **Trend-copying without a twist:** Same trending audio, same format everyone else is using — noise.
- **Lacks specificity:** "Life is hard sometimes" vs "I cried in a Tesco car park at 3pm on a Tuesday." Specificity is what makes things feel real.

### The 9 Devices

**1. THE QUESTION — a mental itch**
Forces the viewer into an open loop the brain must resolve. Avoid yes/no questions. Use what, why, how, when did, or which. Force comparison. Create introspection without resolution — the most powerful questions have no single right answer.

Examples that work:
- "Which Disney princess messed up millennial women the most?" (@vicbrugger) — forces viewer to mentally run through every princess. Specificity makes it irresistible.
- "Was it worth it to be happy for a little bit even though it ended up sad?" (@jonas.luskey) — no right answer. Forces introspection.
- "Is it possible to make an entire business in one day and make our first $1000 off of it?" (@minolee.mp4) — stakes + timeframe + curiosity.
- "Ever wonder what it's like to be mixed race?" (@emilyannwillcox) — identity question rarely asked out loud.

Template: "Which [specific category] [action] [specific group] the most?" or "What if [relatable scenario] but with [unexpected twist]?"

**2. THE GUT-PUNCH — WOAH moment**
Emotional arousal captures attention. Puncture a romantic ideal by colliding it with reality. Lead with the emotional conclusion, let the viewer wonder why.

Examples that work:
- "The elite will never accept you. No matter what you do." (@maisonrickie) — absolute statement that challenges aspiration culture.
- "Everyone is an artist until the rent is due." (@bailey.schildbach) — romantic ideal meets financial reality.
- "I don't know how to explain it but I feel like something special was stolen from me." (@shibustuff) — vague enough to be universal, viewer fills in their own loss.
- "I love corporate slop bowls. They fuel my body and soul so I can be a productive worker." (@citiesbydiana) — sarcasm so dry it reads as sincerity for a split second.

Template: "Everyone [universal subject] is [idealized thing] until [harsh reality]" or "I don't know how to explain it but [vague yet universal feeling]"

**3. THE METAPHOR — you feel before you understand**
Bypasses rational processing. Combine absurdity with vulnerability — absurdity stops the scroll, vulnerability keeps it. Build extended metaphors with layered clauses.

Examples that work:
- "Money is like sea water, the more you drink, the thirstier you get." (@vicbrugger) — classic paradox structure.
- "Making friends in your mid twenties is like showing up to a sex party in crocs and asking if there's a signup sheet." (@emilyannwillcox) — absurd metaphor + vulnerability. So specific it becomes universal.
- "If corporate office is where dreams go to die and men go to bald then the tube of London is the funeral procession." (@kristof.oro) — extended metaphor that builds momentum.
- "The people that built their heaven on land is telling you that yours is in the sky." (@just.randee) — political commentary disguised as poetry.

Template: "[Complex experience] is like [absurdly specific scenario]" or "[X] is where [Y] happens and [Z] happens, therefore [X] is [unexpected conclusion]"

**4. THE CONFESSION — disarming, risk and reward**
Triggers the reciprocity principle. Flip the expected reaction. Bait-and-switch. Sometimes the simplest confession hits hardest — don't underestimate raw unadorned truth.

Examples that work:
- "I'm at the age where if I got a girl pregnant my mom wouldn't be disappointed but I would." (@brandongrogran) — flips the expected reaction.
- "I'm ashamed to meet my girlfriend's friends at dinner because I have this contagious disease. HOLY unemployment." (@aungsett_) — bait-and-switch reframes unemployment as contagious.
- "I'm in my 30s and I'm single and I have no idea what I'm doing with my life." (@dannyxtorres) — no gimmick, raw truth.
- "I've been pretending to like my life for two years." — devastating in simplicity.

Template: "I'm at the age where [expected reaction] but actually [honest reaction]" or "I've been pretending to [socially acceptable stance] for [timeframe]"

**5. THE NARRATOR — I'm sat**
Humans are hardwired for narrative. Signal that a story is coming and the brain shifts into a different mode of attention. Start with a universal experience. Use hyper-specific backstory to build trust. Past tense signals transformation is coming.

Examples that work:
- "I was up last night thinking of all the embarrassing things I've done in my life…" (@brandongrogran1) — universal late-night experience.
- "4 years ago I thought the meaning of life was getting a girlfriend. I was a late blooming 17 year old who spent his high school years watching anime and playing league of legends." (@minolee.mp4) — hyper-specific backstory feels like the start of a movie.
- "For the longest time I thought I was scared of love." (@noellehamoen) — opens a door to a revelation. Past tense promises a twist.
- "One day, you realize you're wearing a scent they never smelled. In an outfit they've never seen. With a side of you they've never met." (@jonas.luskey) — cinematic narration, each clause pulls you deeper.

Template: "For the longest time I thought [belief]..." or "One day, you realize [quiet revelation]"

**6. THE DECLARATION — bold and self-assured**
State your take as fact, not opinion. No "I think" or "maybe." The bolder the claim, the more engagement it generates. You don't need to be right — you need to be convicted.

Examples that work:
- "The biggest predictor of success isn't intelligence, it's this: high agency." (@lindsiannshi) — challenges a deeply held assumption.
- "Being unemployed is the sexiest thing you can be right now." (@viepsa) — contrarian flex, reframes stigma as desirable.
- "Men are just propaganda to distract women from reaching their full potential." (@theelliebarker) — incendiary take with deadpan conviction.
- "I'm done being polite about this." — promise of unfiltered honesty.

Template: "The biggest predictor of [outcome] isn't [conventional factor], it's [unexpected factor]: [reveal]" or "I'm done being [polite stance] about [topic]"

**7. THE PARADOX — instant tension**
Logical impossibility that somehow makes sense. Brain short-circuits trying to resolve it.

Examples that work:
- "Imagine marrying someone so ugly that all they have is looks." (@shifu.razif) — impossible that somehow makes sense.
- "Because there are already enough impressive people in the world, let me not be one of them." (@sean4chen) — anti-ambition framed as wisdom.
- "An entire generation is currently studying for jobs that won't exist, and taking on 6 figure debt to do so." (@rpn) — scale + absurdity, feels urgent.
- "Getting everything I ever wanted has been a profoundly disappointing experience." (@emilyannwillcox) — ultimate paradox, challenges the narrative everyone's been sold.

**8. THE PROPHECY — urgency + authority**
Taps into the human desire for certainty in uncertain times. Creates FOMO. Promise transformation through a single specific shift.

Examples that work:
- "If you can master this one mindset shift you will be in the 1%." (@blairrichardsofficial) — specificity ("one mindset shift") makes it feel actionable.
- "I stopped working on myself and it's the best thing I've ever done." (@moya.palk) — anti-self-help prophecy attacks the dominant narrative.
- "In five years, nobody will remember this advice." — meta-commentary that undermines its own authority.

**9. THE CONTRARIAN — challenge assumptions**
Disrupts pattern recognition. When a viewer has seen "consistency is key" a hundred times, "consistency is overrated" forces a reassessment.

Examples that work:
- "Consistency is overrated. Anyone can find success in repetition." (@1vstvows) — attacks sacred advice.
- "You don't hate capitalism. What you hate is not being on top of it." (@vicbrugger) — reframes entire anti-capitalist discourse in one sentence.
- "Going viral is making you broke." (@meagnunez) — attacks the thing every creator chases.
- "The key to getting what you want is letting go of what you want." (@americanbaron) — zen koan energy.

Template: "You don't hate [X]. What you hate is [reframe]." or "Consistency is overrated. [Reframe of sacred advice]."

---

## Competitor Strategy Note Rule

Every post must have a `strategy_note` that names: (1) which hook device was used and why it fits this specific post, and (2) what competitor signal or top-performing pattern informed the content. If pulling from @soberglowup_ or @neuro.liminal, name the account and the specific tactic being adapted.

---

## Top-Performing Content Patterns (Own Data)

1. **Radical Inclusivity:** 9,472 likes, 269 comments. All-pathways, zero-gatekeeping. People share to a struggling friend. Broad reach; the core ICP is past this stage.
2. **Educational with specific numbers:** 4,041 likes. Real data tied to a personal recovery moment.
3. **Contrarian take:** 776 likes, 34 comments. Personal experience stated as fact. "IF and only if" language. Forces people to pick a side.
4. **Dark humor:** 386 likes. One-joke format. High-functioning addiction universal experience.
5. **Recovery and place connection:** 235 likes. SE Asia or Thai cultural context connected to a recovery moment.

**What kills engagement:** Thesis posts ("X traits make you Y"). Generic sober community content. Content any sober creator could post with no personal anchor.

---

## Competitor Context

**@soberglowup_** and **@neuro.liminal** are scraped weekly via Apify. Identify what content formats drive their paid products, find where they are NOT serving the ambitious rebuilder ICP with specific freelance education, and build at least one post per week in that gap.

Lexi's differentiation: raw personal story + income rebuild specificity + SE Asia location + LGBTQ+ identity + hyper-specific freelance education neither competitor provides.

---

## Notion Database Fields

The soberadventuring Notion DB (`379b8973a3ad81f68b6dd65cc244a852`):

| Field | Content |
|-------|---------|
| Title | Post title |
| Date | YYYY-MM-DD |
| Platform | Instagram |
| Content Type | Educational / Personal Story / Tips & Practical / Contrarian Take / Failure Archive / Building In Public / Travel |
| Post Format | carousel / talking head |
| Status | Draft |
| Pillar | text |
| Hook / Caption Draft | Slide 1 text |
| Caption | Full caption |
| Post Strategy | COMMENTS / SHARES / SAVES |
| Device Used | Hook device name (e.g. The Confession) |

Slides 2-6 are written as numbered block children on the page body.

---

## Known Issues and Fixes

- **Windows UTF-8:** `sys.stdout.reconfigure(encoding='utf-8')` in `main.py` prevents encoding crashes.
- **JSON trailing commas:** `re.sub(r',\s*([}\]])', r'\1', raw)` in `_parse_json()` strips commas Claude Opus occasionally adds.
- **Wrong database:** Never write to `37cb8973...` (Alderwood). Always use `NOTION_PARENT_PAGE_ID` from `.env`.
- **Fabricated content:** Never invent specific personal incidents. Use [BRACKET PLACEHOLDERS].
- **Device Used field:** If the Notion field doesn't exist yet, notion_output.py retries without it automatically.
