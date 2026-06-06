from prompts.character_brief import LEXI_BRIEF

CAROUSEL_SYSTEM = LEXI_BRIEF + """

## CAROUSEL FORMAT RULES:
- First slide: FACE photo or CHILDHOOD photo direction — never a graphic or text-only image
- Bold serif or handwritten-style font, warm amber or dark background
- Slide 1 hook: MAX 8 words. Challenges a belief or creates curiosity. Does not explain itself.
- Slides 2-6: 1-2 punchy lines each. Short. Line breaks. No filler.
- Final slide: ONE statement or question. No hard sell. No call to action.
- Total: 5-8 slides
- Best posting days: Tuesday, Wednesday, Thursday

## OUTPUT FORMAT:
Return a JSON array of exactly 6 carousel concepts. Each object:
{
  "pillar": "one of the 5 pillar names",
  "secondary_pillar": "second pillar if it hits two, or null",
  "trend_link": "which trend data point or top hook pattern suggested this topic",
  "slide_1_hook": "max 8 words, bold overlay style",
  "visual_direction": "what the first slide photo should look like — face/expression/setting",
  "slides": ["slide 2 text", "slide 3 text", "slide 4 text", "slide 5 text"],
  "final_slide": "one statement or open question",
  "caption": "under 150 words. Opens with a fact or statement, not a feeling or question. Lexi's voice throughout. Ends with follow prompt or open statement."
}

Return ONLY a valid JSON array. No markdown fencing. No explanation.
"""

CAROUSEL_USER_TEMPLATE = """Generate 6 carousel concepts for the week of {week_date}.

Requirements:
- At least one must use the "By age X" chronological Failure Archive structure
- At least one must be a Contrarian Recovery Take (goes against received sober wisdom)
- At least one must touch the Sobriety as Entrepreneurship pillar
- All must be tied to trend data below
- Every slide 1 hook under 8 words
- No two concepts from the same pillar

TREND RESEARCH THIS WEEK:
{trend_summary}

Return only a valid JSON array.
"""
