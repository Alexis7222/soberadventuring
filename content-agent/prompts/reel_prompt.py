from prompts.character_brief import LEXI_BRIEF

REEL_SYSTEM = LEXI_BRIEF + """

## 6-9 SECOND REEL FORMAT RULES:
- Hook must land in the first 2 seconds — if it needs context, it's already dead
- Text overlay only, OR text + face — no production required
- One single relatable moment — no context needed to understand it
- Works on a cold audience who has never seen Lexi before
- Audio carries the emotional weight — suggest mood, not specific song title
- Best posting days: Thursday, Friday, Saturday

## OUTPUT FORMAT:
Return a JSON array of reel concepts. Each object:
{
  "pillar": "one of the 5 pillar names",
  "calendar_topic": "title of the TikTok calendar topic this scripts, or 'original' if none",
  "text_overlay": "max 8 words — this is what appears on screen",
  "visual_direction": "what is physically happening on screen — face, location, action. Specific.",
  "audio_mood": "emotional tone or genre — e.g. nostalgic indie, deadpan silence, chaotic Y2K pop",
  "why_now": "one line: why this format is working right now based on trend data"
}

Return ONLY a valid JSON array. No markdown fencing. No explanation.
"""

REEL_CALENDAR_SECTION = """TIKTOK TOPICS FROM NOTION — script these specifically (one reel per topic):
{topic_list}

Generate exactly {count} reel scripts — one per TikTok calendar topic above.
Use the "Seed draft" as the hook direction — expand into a 6-9 second format.
Set "calendar_topic" field to the title of the topic it scripts."""

REEL_FREEFORM_SECTION = """NO TIKTOK CALENDAR TOPICS FOUND — generate 4 original reel concepts.

Requirements:
- Mix of pillars — no two from the same pillar
- At least one must be darkly funny
- At least one must use a before/after contrast (active addiction vs now)
- Audio mood must match the emotional tone of the overlay text
- Every concept must work for a completely cold audience — no prior knowledge of Lexi needed

Set "calendar_topic" to "original" for all 4."""

REEL_USER_TEMPLATE = """Generate reel scripts for the week of {week_date}.

{calendar_section}

LEXI'S OWN TOP PERFORMING POSTS THIS WEEK (use as signal for what's resonating with her audience):
{own_posts_summary}

TREND RESEARCH THIS WEEK (niche-wide):
{trend_summary}

Return only a valid JSON array.
"""
