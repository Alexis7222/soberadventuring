from prompts.character_brief import LEXI_BRIEF
from prompts.gold_vault import GOLD_VAULT_PROMPT

CAROUSEL_SYSTEM = LEXI_BRIEF + "\n\n" + GOLD_VAULT_PROMPT + """

## OUTPUT FORMAT
Return a JSON array of carousel concepts. Each object must match the structure of the gold vault posts exactly.

{
  "format": "FORMAT_A_MEMOIR_CHAPTERS or FORMAT_B_CONTRARIAN_REASONS",
  "pillar": "one of the 5 pillar names",
  "calendar_topic": "title of the calendar topic this scripts, or 'original' if no calendar",
  "performance_pattern": "which gold vault pattern this replicates and why",
  "cover_hook": "max 8 words — the title overlay on slide 1",
  "cover_visual": "describe the slide 1 photo — face selfie, childhood photo, or other. Be specific about expression, setting, mood.",
  "slides": [
    {
      "header": "Chapter name (2-5 words) — for Format A: clinical or experiential label. For Format B: the reason stated as a short phrase.",
      "text": "Body text for this slide. 1-3 sentences max. Lexi's voice. Specific detail only she could give.",
      "visual": "Photo direction for this slide — what's in the image, mood, setting."
    }
  ],
  "caption": "Under 150 words. Opens with specific fact or statement — never a question, never an emotion. Lexi's voice throughout. Ends with one follow prompt, open statement, or 'IF and only if' qualifier. No emoji sign-off.",
  "share_hook": "One sentence: why would someone send this to a specific person in their life?"
}

CRITICAL FORMAT RULES:
- "slides" array does NOT include the cover slide — that is covered by cover_hook and cover_visual
- Every slide must have a header (short chapter name) AND body text AND visual direction
- Format A slides: chapter headers are clinical labels OR experiential names (Wild Delusions, Conduct disorder, Codependency)
- Format B slides: chapter headers are the reason stated as a phrase (NA beverages slap!, To set an example)
- Final slide in the array is always the closing slide
- Body text per slide: 1-3 sentences, specific detail, voice is always Lexi's

Return ONLY a valid JSON array. No markdown fencing. No explanation.
"""

CAROUSEL_CALENDAR_SECTION = """CONTENT CALENDAR FROM NOTION — script these topics specifically (one carousel per topic):
{topic_list}

Generate exactly {count} carousel scripts — one per calendar topic above.
Match each carousel's pillar, content_type, and feeds_offer to its calendar topic.
Use the "Seed draft" as creative direction — expand it into a full carousel using Format A or Format B from the gold vault.
Set "calendar_topic" field to the title of the topic it scripts."""

CAROUSEL_FREEFORM_SECTION = """NO CALENDAR TOPICS FOUND — generate 6 original carousel concepts.

MANDATORY DISTRIBUTION — every run, no exceptions:
- 2 must use Format A (memoir chapters) — one with childhood photo cover, one with raw current Lexi face
- 2 must use Format B (contrarian reasons) — "N reasons I [do thing most sober people avoid]"
- 1 must be the radical inclusivity / "I'm just glad you're here" pattern — all recovery pathways, zero gatekeeping
- 1 must lead with a clinical label + absurd personal example (the Miley Cyrus / disco floor / Acacia twin formula)

Set "calendar_topic" to "original" for all 6."""

CAROUSEL_USER_TEMPLATE = """Generate carousel scripts for the week of {week_date}.

{calendar_section}

LEXI'S OWN TOP PERFORMING POSTS THIS WEEK (use as primary signal — what's resonating with her audience right now):
{own_posts_summary}

Rules for every carousel:
- Every cover_hook under 8 words
- Every carousel must require Lexi's specific history, numbers, or location — if any sober creator could post it, rewrite it
- Photo directions must be specific — not "face photo" but "close-up mirror selfie, dark outfit, serious expression, tattoo visible"
- Chapter headers must be 2-5 words max
- Body text must have at least one specific detail only Lexi could provide (a real name, a real number, a real place, a real absurd incident)

TREND RESEARCH THIS WEEK (niche-wide):
{trend_summary}

Return only a valid JSON array.
"""
