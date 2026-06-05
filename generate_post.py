import anthropic
import os
import json
import re
from datetime import date
from pathlib import Path

# ── SEO-researched topic rotation (35 titles from keyword report) ──
TOPICS = [
    # Sobriety / Lifestyle
    {"title": "What Nobody Tells You About the First 30 Days of Sobriety",          "keyword": "early sobriety first 30 days sober",                            "category": "Recovery"},
    {"title": "What Happens to Your Body When You Stop Drinking (Week by Week)",    "keyword": "what happens when you stop drinking",                           "category": "Recovery"},
    {"title": "Sober Curious vs. Sober: What's the Difference and Which One Are You?", "keyword": "sober curious meaning sober curious vs sober",             "category": "Recovery"},
    {"title": "Benefits of Sobriety at 30, 60, and 90 Days — A Real Timeline",     "keyword": "benefits of sobriety sobriety timeline",                       "category": "Recovery"},
    {"title": "How to Get Sober Without Rock Bottom (You Don't Have to Wait)",      "keyword": "how to get sober sobriety tips",                               "category": "Recovery"},
    {"title": "What Does It Actually Feel Like to Be Sober? Honest Answers",        "keyword": "sober lifestyle what is sobriety",                             "category": "Recovery"},
    {"title": "How to Stop Drinking Alcohol on Your Own: A Practical Guide",        "keyword": "how to stop drinking on my own",                               "category": "Recovery"},
    {"title": "When Do Cravings Go Away? What to Expect in Early Recovery",         "keyword": "when do cravings stop early sobriety symptoms",                "category": "Recovery"},
    {"title": "Dry January vs. Permanent Sobriety: Which One Is Right for You?",   "keyword": "dry January sober curious movement",                           "category": "Recovery"},
    {"title": "Alcohol and Anxiety: Why Getting Sober Might Be the Fix",            "keyword": "alcohol and anxiety sobriety benefits",                        "category": "Recovery"},
    # Sobriety Coaching
    {"title": "What Does a Sobriety Coach Actually Do? (It's Not Therapy)",         "keyword": "sobriety coach what is sobriety coaching",                     "category": "Sobriety Coaching"},
    {"title": "Sobriety Coach vs. Therapist vs. AA: Which Support Is Right for You?", "keyword": "sobriety coach vs therapy alternatives to AA",             "category": "Sobriety Coaching"},
    {"title": "How Much Does a Sober Coach Cost? Breaking Down the Investment",     "keyword": "sobriety coach cost sober coach online",                       "category": "Sobriety Coaching"},
    {"title": "5 Signs You Might Benefit From a Sobriety Coach",                    "keyword": "sobriety coaching alcohol free coaching",                      "category": "Sobriety Coaching"},
    {"title": "Can You Get Sober Online? What Remote Sobriety Coaching Looks Like", "keyword": "online sobriety support sober coach online",                   "category": "Sobriety Coaching"},
    {"title": "The ALIVE Method: My Approach to Sobriety Coaching",                 "keyword": "sobriety coaching sobriety framework ALIVE method",            "category": "Sobriety Coaching"},
    {"title": "How I Help People Build a Sober Life They Actually Want to Live",    "keyword": "sobriety coach sober accountability coach",                    "category": "Sobriety Coaching"},
    # Sober Travel
    {"title": "The Complete Guide to Sober Travel: Best Trip of Your Life",         "keyword": "sober travel sober travel tips",                               "category": "Sober Travel"},
    {"title": "Sober in Chiang Mai: A Digital Nomad's Guide to Thriving Without Alcohol", "keyword": "sober in Thailand sober travel digital nomad",         "category": "Sober Travel"},
    {"title": "How to Handle Social Drinking While Traveling (Without Caving)",     "keyword": "how to travel sober sober travel tips",                        "category": "Sober Travel"},
    {"title": "The Best Destinations for Sober Travel in Southeast Asia",           "keyword": "sober travel alcohol free vacation Southeast Asia",             "category": "Sober Travel"},
    {"title": "Dry Tripping: What It Is and Why Gen Z Is Leading This Revolution",  "keyword": "dry tripping sober travel trend",                              "category": "Sober Travel"},
    {"title": "Can You Be a Digital Nomad and Stay Sober? Yes — Here's How",       "keyword": "digital nomad sober traveling in recovery",                    "category": "Sober Travel"},
    {"title": "Sober Travel Packing List: Everything I Bring to Stay Grounded",     "keyword": "sober travel blog sober travel tips packing",                  "category": "Sober Travel"},
    {"title": "What Happened When I Traveled to 10 Countries Sober",               "keyword": "sober travel blog traveling in recovery honest",               "category": "Sober Travel"},
    # Non-12-Step / Secular
    {"title": "Can You Get Sober Without AA? Yes — Here's What That Looks Like",   "keyword": "sobriety without AA alternatives to AA",                       "category": "Recovery"},
    {"title": "Non-12-Step Recovery: Every Alternative Explained",                  "keyword": "non 12 step recovery alternatives to AA SMART LifeRing",       "category": "Recovery"},
    {"title": "How to Get Sober If You're Not Religious",                           "keyword": "non religious sobriety secular sobriety no higher power",      "category": "Recovery"},
    {"title": "Is There a Sobriety Group for Atheists and Agnostics? Yes — Several","keyword": "atheist sobriety secular sobriety alternatives to AA",         "category": "Recovery"},
    {"title": "SMART Recovery vs. AA: An Honest Comparison",                        "keyword": "SMART recovery non 12 step recovery vs AA",                    "category": "Recovery"},
    {"title": "Why I'm Building a Secular Recovery Community (And Who It's For)",   "keyword": "secular sobriety non religious sobriety recovery community",    "category": "Recovery"},
    {"title": "The Problem With Traditional Recovery Spaces (And What We're Doing Instead)", "keyword": "alternatives to AA non religious sobriety",          "category": "Recovery"},
    # Freelance / Lifestyle
    {"title": "How I Quit Drinking and Built a Freelance Business From Scratch",    "keyword": "sober freelance sobriety lifestyle career change Upwork",      "category": "Freelance"},
    {"title": "The Sober Pivot: Why Getting Sober Was the Best Career Move I Made", "keyword": "sobriety benefits sober lifestyle career sobriety tips",       "category": "Freelance"},
    {"title": "How to Start Freelancing on Upwork With No Experience",              "keyword": "how to start freelancing on Upwork with no experience",        "category": "Freelance"},
]

SYSTEM_PROMPT = """You write blog posts for soberadventuring.com — Alexis Antonelli's site.

══ WHO ALEXIS IS ══
Got sober again at 24. No fanfare, no treatment center — just a Tuesday decision.
9 years in recovery spaces: recovery support specialist, ABA therapist, case manager, sober house manager.
Cycled through 20+ jobs before freelancing. No clean resume. Made it work anyway.
Made $30k in first 4 months on Upwork starting from zero.
Now runs Impello Agency and coaches high-potential people, living in Chiang Mai, Thailand.
Non-12-step, harm reduction, motivational interviewing, trauma-informed. All pathways to recovery supported.
Not a licensed therapist — a person who went through something hard, found a way forward, and shares what actually worked.

══ VOICE — STUDY THESE EXACT EXAMPLES. MATCH THIS. ══
"I got sober again at 24. No fanfare, no treatment center — just a Tuesday where I decided I was done."
"What followed wasn't a clean upward arc. It was the slow, unglamorous process of trying to figure out who I was without the thing that had organized my entire personality."
"Fired, quit, ghosted, burned out — whatever the reason, I'd accumulated a record that no hiring manager was going to overlook."
"I made $30k within my first 4 months. Not because I had the perfect background. Because I understood what the client actually needed and I could communicate it clearly."
"Sobriety didn't fix everything. But it gave me access to myself — my actual thinking, my real capacity — for the first time in years."
"The content that existed either treated sobriety like a clinical condition or a spiritual awakening. I needed someone to tell me how to actually rebuild — practically, step by step, without pretending it wasn't hard."

Voice rules — these are non-negotiable:
- First person. Always.
- Short sentences. Sentence fragments when they land harder. "Not because X. Because Y." is a good pattern.
- Specific and concrete. Real numbers, real timelines, real situations.
- No filler sentences. Every sentence earns its place. If it doesn't add anything, cut it.
- Warm but direct. Not clinical. Not preachy. Not self-help-book energy.
- Occasionally blunt. That's the brand.
- Never moralize. Never lecture. Describe what happened, what worked, what didn't.
- Do not wrap up sections with "the key takeaway is" or motivational summaries.

══ BANNED PHRASES — NEVER WRITE ANY OF THESE ══
delve into, delve deeper, it's important to note, in conclusion, to summarize, furthermore, moreover, additionally (as a paragraph opener), navigate (metaphorically), game-changer, transformative, journey (especially "recovery journey" or "freelance journey"), tapestry, in today's world, in today's fast-paced world, let's explore, holistic approach, leverage (as a verb for non-physical things), multifaceted, in essence, it goes without saying, needless to say, I cannot stress enough, at the end of the day, when it comes to, it's worth noting, comprehensive, robust, paramount, seamlessly, beacon, foster (as in "foster growth"), pivotal, embark on, realm, testament to, underscores the importance, unpack, dive into, dive deep, circle back, moving forward, the bottom line is, with that said, without further ado, having said that, it's crucial that, one thing to keep in mind

Also avoid:
- Starting a paragraph with a rhetorical question used as a hook ("Are you tired of feeling stuck?")
- Padding openers: "When it comes to X..." / "One important thing to consider..."
- Perfect parallel structure in every single list item — sounds robotic
- Closing a section with a motivational one-liner

══ STRUCTURE ══
intro: 2-3 sentences. Hook immediately. Drop the reader into the real thing. No throat-clearing.
sections: 3-5 sections with H2 headings. Each: 2-4 substantive paragraphs. No filler.
conclusion: 2-3 sentences. Honest, not hype. Soft CTA with internal link as raw HTML <a href="URL">text</a>.
Total: ~1000 words.
Include the target keyword naturally in the first 100 words and in one H2 heading.

══ INTERNAL LINKS — weave in where genuinely natural ══
Free clarity call: https://calendly.com/alexis-m-antonelli/freediscoverycall
Telegram recovery group: https://t.me/+wJbhwv2ccS1hMjFh
Upwork Starter Guide ($14.99): https://antonelli74.gumroad.com/l/wfbmpv
The PIVOT Method: https://soberadventuring.com/method/
About Alexis: https://soberadventuring.com/story/

Output ONLY valid JSON — no markdown fences, no extra text before or after:
{
  "title": "SEO title under 60 chars, includes keyword",
  "meta_description": "155-160 chars, includes keyword, sounds human not robotic",
  "slug": "url-slug-with-hyphens",
  "reading_time": 6,
  "intro": "2-3 sentence hook in Alexis voice.",
  "sections": [
    {"heading": "H2 text", "paragraphs": ["paragraph 1", "paragraph 2", "paragraph 3"]}
  ],
  "conclusion": "2-3 sentences. Soft CTA with HTML <a href='URL'>anchor text</a> embedded."
}"""


def get_topic():
    day = date.today().timetuple().tm_yday
    return TOPICS[day % len(TOPICS)]


def call_claude(topic):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": (
                f"Write a blog post with this title: \"{topic['title']}\"\n"
                f"Target keyword(s): {topic['keyword']}\n"
                f"Category: {topic['category']}\n\n"
                "Remember: write in Alexis's exact voice. Short sentences. Real specifics. "
                "No AI filler phrases. No motivational padding."
            )
        }]
    )
    text = msg.content[0].text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def render_post_html(data, topic, post_date_str):
    slug = data["slug"]
    category = topic["category"]

    sections_html = ""
    for s in data["sections"]:
        paras = "".join(f"<p>{p}</p>" for p in s["paragraphs"])
        sections_html += f'<h2 class="post-h2">{s["heading"]}</h2>\n{paras}\n'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{data['title']} · Sober Adventuring</title>
<meta name="description" content="{data['meta_description']}">
<meta property="og:title" content="{data['title']} · Sober Adventuring">
<meta property="og:description" content="{data['meta_description']}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://soberadventuring.com/blog/{slug}/">
<link rel="canonical" href="https://soberadventuring.com/blog/{slug}/">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{data['title']}",
  "description": "{data['meta_description']}",
  "datePublished": "{post_date_str}",
  "author": {{"@type": "Person", "name": "Alexis Antonelli", "url": "https://soberadventuring.com"}},
  "publisher": {{"@type": "Organization", "name": "Sober Adventuring", "url": "https://soberadventuring.com"}},
  "url": "https://soberadventuring.com/blog/{slug}/"
}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Bricolage+Grotesque:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--ink:#1B0009;--forest:#2D3D24;--terra:#C5442C;--cream:#F4E8D0;--paper:#F0EDE8;--white:#FEFCF8;--muted:#6b5a4e}}
html{{scroll-behavior:smooth}}
body{{background:var(--paper);color:var(--ink);font-family:'Bricolage Grotesque',sans-serif;font-size:16px;line-height:1.7;-webkit-font-smoothing:antialiased}}
.back-nav{{background:var(--forest);padding:14px 28px;display:flex;align-items:center;justify-content:space-between}}
.back-nav a{{font-size:13px;font-weight:600;color:var(--cream);text-decoration:none;opacity:0.8}}
.back-nav a:hover{{opacity:1}}
.back-nav .site-name{{font-family:'DM Serif Display',serif;font-size:15px;color:var(--cream);opacity:0.45}}
.post-hero{{background:var(--ink);padding:64px 28px 52px;text-align:center}}
.post-category{{font-size:11px;font-weight:600;letter-spacing:0.18em;text-transform:uppercase;color:var(--terra);margin-bottom:18px}}
.post-hero h1{{font-family:'DM Serif Display',serif;font-size:clamp(28px,6vw,52px);line-height:1.05;letter-spacing:-0.02em;color:var(--cream);margin-bottom:16px}}
.post-meta{{font-size:13px;color:rgba(244,232,208,0.4);letter-spacing:0.04em}}
.post-body{{max-width:680px;margin:0 auto;padding:56px 28px 80px}}
.post-intro{{font-size:18px;line-height:1.8;color:var(--ink);margin-bottom:40px;font-family:'DM Serif Display',serif;font-style:italic}}
.post-h2{{font-family:'DM Serif Display',serif;font-size:clamp(22px,4vw,30px);line-height:1.1;letter-spacing:-0.02em;color:var(--ink);margin:48px 0 16px;padding-top:8px;border-top:1px solid rgba(27,0,9,0.08)}}
p{{font-size:16px;line-height:1.85;color:var(--ink);margin-bottom:20px}}
a{{color:var(--terra);font-weight:600}}
.post-conclusion{{margin-top:48px;padding:28px 32px;background:var(--white);border-left:3px solid var(--terra);font-size:16px;line-height:1.8}}
.post-cta{{background:var(--forest);padding:52px 28px;text-align:center;margin-top:0}}
.post-cta h2{{font-family:'DM Serif Display',serif;font-size:clamp(24px,5vw,36px);color:var(--cream);margin-bottom:10px;line-height:1.1}}
.post-cta p{{font-size:15px;color:rgba(244,232,208,0.6);max-width:400px;margin:0 auto 28px;line-height:1.65}}
.btn{{display:inline-block;background:var(--terra);color:var(--cream);font-family:'Bricolage Grotesque',sans-serif;font-size:14px;font-weight:700;text-decoration:none;padding:14px 28px}}
@media(max-width:640px){{.post-body{{padding:44px 20px 64px}}.post-hero{{padding:44px 20px 40px}}.back-nav{{padding:12px 20px}}}}
</style>
</head>
<body>

<div class="back-nav">
  <a href="/">&#8592; soberadventuring.com</a>
  <span class="site-name">Sober<em style="font-style:italic;color:#C5442C">Adventuring.</em></span>
</div>

<div class="post-hero">
  <p class="post-category">{category}</p>
  <h1>{data['title']}</h1>
  <p class="post-meta">By Alexis &nbsp;·&nbsp; {post_date_str} &nbsp;·&nbsp; {data['reading_time']} min read</p>
</div>

<div class="post-body">
  <p class="post-intro">{data['intro']}</p>

  {sections_html}

  <div class="post-conclusion">
    <p>{data['conclusion']}</p>
  </div>
</div>

<div class="post-cta">
  <h2>Want to talk it through?</h2>
  <p>20 minutes, free. We figure out where you are and what the actual next move looks like.</p>
  <a href="https://calendly.com/alexis-m-antonelli/freediscoverycall" class="btn">Book the free clarity call &rarr;</a>
</div>

</body>
</html>"""


def render_index_html(posts):
    cards = ""
    for p in reversed(posts):
        cards += f"""
    <a href="/blog/{p['slug']}/" class="post-card">
      <span class="card-cat">{p['category']}</span>
      <h2 class="card-title">{p['title']}</h2>
      <p class="card-meta">{p['date']} &nbsp;·&nbsp; {p['reading_time']} min read</p>
      <p class="card-desc">{p['meta_description']}</p>
      <span class="card-link">Read &rarr;</span>
    </a>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Blog · Sober Adventuring</title>
<meta name="description" content="Recovery, freelancing, and sober living — honest articles from Alexis at Sober Adventuring.">
<link rel="canonical" href="https://soberadventuring.com/blog/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Bricolage+Grotesque:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--ink:#1B0009;--forest:#2D3D24;--terra:#C5442C;--cream:#F4E8D0;--paper:#F0EDE8;--white:#FEFCF8;--muted:#6b5a4e}}
body{{background:var(--paper);color:var(--ink);font-family:'Bricolage Grotesque',sans-serif;-webkit-font-smoothing:antialiased}}
.back-nav{{background:var(--forest);padding:14px 28px;display:flex;align-items:center;justify-content:space-between}}
.back-nav a{{font-size:13px;font-weight:600;color:var(--cream);text-decoration:none;opacity:0.8}}
.back-nav .site-name{{font-family:'DM Serif Display',serif;font-size:15px;color:var(--cream);opacity:0.45}}
.blog-hero{{background:var(--ink);padding:64px 28px 52px;text-align:center}}
.blog-hero h1{{font-family:'DM Serif Display',serif;font-size:clamp(34px,7vw,56px);line-height:1.0;letter-spacing:-0.025em;color:var(--cream);margin-bottom:12px}}
.blog-hero h1 em{{color:var(--terra);font-style:italic}}
.blog-hero p{{font-size:16px;color:rgba(244,232,208,0.5);max-width:420px;margin:0 auto;font-family:'DM Serif Display',serif;font-style:italic}}
.blog-grid{{max-width:900px;margin:0 auto;padding:56px 28px 80px;display:grid;grid-template-columns:1fr 1fr;gap:20px}}
@media(max-width:640px){{.blog-grid{{grid-template-columns:1fr;padding:40px 20px 64px}}}}
.post-card{{background:var(--white);border:1.5px solid rgba(27,0,9,0.1);padding:28px;text-decoration:none;display:flex;flex-direction:column;gap:10px;transition:border-color 0.15s,transform 0.15s}}
.post-card:hover{{border-color:var(--terra);transform:translateY(-2px)}}
.card-cat{{font-size:10px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:var(--terra)}}
.card-title{{font-family:'DM Serif Display',serif;font-size:20px;line-height:1.15;letter-spacing:-0.01em;color:var(--ink)}}
.card-meta{{font-size:11px;color:var(--muted);letter-spacing:0.04em}}
.card-desc{{font-size:13px;color:var(--muted);line-height:1.65;flex:1}}
.card-link{{font-size:13px;font-weight:700;color:var(--terra);margin-top:4px}}
</style>
</head>
<body>

<div class="back-nav">
  <a href="/">&#8592; soberadventuring.com</a>
  <span class="site-name">Sober<em style="font-style:italic;color:#C5442C">Adventuring.</em></span>
</div>

<div class="blog-hero">
  <h1>Real talk.<br><em>No fluff.</em></h1>
  <p>Recovery, freelancing, and building a life worth being present for.</p>
</div>

<div class="blog-grid">
  {cards}
</div>

</body>
</html>"""


def main():
    topic = get_topic()
    print(f"Generating post for: {topic['title']}")

    data = call_claude(topic)
    print(f"Title: {data['title']}")
    print(f"Slug:  {data['slug']}")

    today = date.today()
    post_date_str = today.strftime("%B %d, %Y")
    post_date_iso = today.isoformat()
    slug = data["slug"]

    post_dir = Path(f"blog/{slug}")
    post_dir.mkdir(parents=True, exist_ok=True)
    post_path = post_dir / "index.html"
    post_path.write_text(render_post_html(data, topic, post_date_str), encoding="utf-8")
    print(f"Wrote: {post_path}")

    posts_json = Path("blog/posts.json")
    posts = json.loads(posts_json.read_text()) if posts_json.exists() else []
    posts = [p for p in posts if p["slug"] != slug]
    posts.append({
        "slug": slug,
        "title": data["title"],
        "meta_description": data["meta_description"],
        "category": topic["category"],
        "date": post_date_iso,
        "reading_time": data["reading_time"],
    })
    posts.sort(key=lambda p: p["date"])
    posts_json.write_text(json.dumps(posts, indent=2), encoding="utf-8")

    blog_index = Path("blog/index.html")
    blog_index.write_text(render_index_html(posts), encoding="utf-8")
    print(f"Updated blog index — {len(posts)} total posts")


if __name__ == "__main__":
    main()
