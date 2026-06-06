from prompts.character_brief import LEXI_BRIEF

MONTHLY_SYSTEM = LEXI_BRIEF + """

## LONG-FORM MUSEUM OF FAILURES FORMAT:
- 10-15 slides total
- Chronological "By age X" or "By [number]" structure throughout
- Escalating dread — each slide should feel worse than the last until the turn
- Specific numbers every time — ten cars, sixteen jobs, $20k debt
- Dark humour embedded in the chaos — stops it being trauma porn
- The identity pivot at the end has to earn the chaos — not just "I got better"
  but who she actually IS now (artist, mentor, consultant, 2 years sober, Thailand)
- First slide hook: creates dread or deep curiosity in under 8 words
- Final slide: identity statement. Present tense. Who she is NOW.

## OUTPUT FORMAT:
Return a single JSON object:
{
  "slide_1_hook": "max 8 words",
  "slides": [
    {
      "slide_number": 2,
      "text": "the actual slide copy — 1-3 lines max",
      "visual": "optional visual direction"
    }
  ],
  "final_slide_identity": "2-3 lines. Present tense. Who she is now.",
  "caption": "under 200 words. Opens with a statement. Ends with an open question designed to get confessional comments — people sharing their own timeline or recognising someone they love."
}

Return ONLY valid JSON. No markdown fencing. No explanation.
"""

MONTHLY_USER_TEMPLATE = """Generate this month's long-form Museum of Failures carousel.

Month: {month_year}
This month's angle: {monthly_angle}

Use her actual known history:
- Arrested by 17
- At 18: level of demoralization doing things for drugs the sober version couldn't imagine
- 16 jobs by age 20, benzo-opioid addiction, couldn't show up for anything
- Dropped out of college 3 times with enough credits for a master's degree
- Hospitalized 10 times, survived two suicide attempts
- 7 cars totaled — doesn't drive anymore ("that's a public service")
- $20k in debt (paid off in sobriety)
- Cannabis-induced psychosis: 14 days without proper sleep, believed she was carrying
  baby Jesus while the government was plotting to assassinate her
- Now: 2 years sober, freelance marketing consultant, Thailand, LGBTQ+, artist, mentor

Build the slide structure around the angle: {monthly_angle}

Return only valid JSON.
"""
