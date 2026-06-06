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
Return a JSON array of exactly 4 reel concepts. Each object:
{
  "pillar": "one of the 5 pillar names",
  "trend_link": "what trend data or hook pattern suggested this",
  "text_overlay": "max 8 words — this is what appears on screen",
  "visual_direction": "what is physically happening on screen — face, location, action",
  "audio_mood": "emotional tone or genre — e.g. nostalgic indie, deadpan silence, chaotic Y2K pop",
  "why_now": "one line: why this specific format is working right now based on trend data"
}

Return ONLY a valid JSON array. No markdown fencing. No explanation.
"""

REEL_USER_TEMPLATE = """Generate 4 x 6-9 second reel concepts for the week of {week_date}.

Requirements:
- Every concept must work for a completely cold audience — no prior knowledge of Lexi needed
- Mix of pillars — no two from the same one
- At least one must be darkly funny
- At least one must use a before/after contrast (active addiction vs now)
- Audio mood must match the emotional tone of the overlay text

TREND RESEARCH THIS WEEK:
{trend_summary}

Return only a valid JSON array.
"""
