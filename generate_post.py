import anthropic
import os
import json
import re
from datetime import date, datetime
from pathlib import Path

# ── Topic rotation ────────────────────────────────────────────────
TOPICS = [
    # Recovery / Sobriety
    {"keyword": "how to get sober without AA", "category": "Recovery"},
    {"keyword": "sober curious what does it mean", "category": "Recovery"},
    {"keyword": "harm reduction approach to sobriety", "category": "Recovery"},
    {"keyword": "early sobriety tips first 90 days", "category": "Recovery"},
    {"keyword": "who am I without alcohol sobriety identity", "category": "Recovery"},
    {"keyword": "sobriety and relationships what actually changes", "category": "Recovery"},
    {"keyword": "non 12 step recovery alternatives to AA", "category": "Recovery"},
    {"keyword": "motivational interviewing sobriety coaching", "category": "Recovery"},
    {"keyword": "trauma informed sobriety coaching", "category": "Recovery"},
    {"keyword": "sober and lonely what to do isolation recovery", "category": "Recovery"},
    {"keyword": "how to build a sober social life", "category": "Recovery"},
    {"keyword": "sobriety and anxiety what helps", "category": "Recovery"},
    # Freelance / Career
    {"keyword": "how to start freelancing on Upwork with no experience", "category": "Freelance"},
    {"keyword": "Upwork profile tips to get your first client", "category": "Freelance"},
    {"keyword": "how to write Upwork proposals that get responses", "category": "Freelance"},
    {"keyword": "freelancing while in recovery sobriety and work", "category": "Freelance"},
    {"keyword": "how to build remote income from scratch", "category": "Freelance"},
    {"keyword": "what skills can I sell on Upwork no experience", "category": "Freelance"},
    {"keyword": "how to get clients as a freelancer beginner", "category": "Freelance"},
    {"keyword": "freelance sales skills how to close clients", "category": "Freelance"},
    # Travel / Lifestyle
    {"keyword": "sober digital nomad how to travel without drinking", "category": "Lifestyle"},
    {"keyword": "living in Chiang Mai Thailand as a freelancer", "category": "Lifestyle"},
    {"keyword": "how to fund full time travel through freelancing", "category": "Lifestyle"},
    {"keyword": "sober travel tips alcohol free travel", "category": "Lifestyle"},
]

SYSTEM_PROMPT = """You write blog posts for soberadventuring.com — Alexis Antonelli's personal site.

About Alexis:
- 2 years fully sober. Got sober again at 24. No treatment center — just a Tuesday decision.
- 9 years in recovery spaces: recovery support specialist, ABA therapist, case manager, sober house manager
- Non-12-step, harm reduction oriented, trauma-informed, motivational interviewing
- Made $30k in first 4 months freelancing on Upwork
- Now runs Impello Agency from Chiang Mai, Thailand
- Voice: warm, direct, honest, real. First person. Not clinical, not preachy. Occasionally blunt.

Internal links to weave in where natural:
- Free clarity call: https://calendly.com/alexis-m-antonelli/freediscoverycall
- Telegram recovery group: https://t.me/+wJbhwv2ccS1hMjFh
- Upwork Starter Guide ($14.99): https://antonelli74.gumroad.com/l/wfbmpv
- The PIVOT Method (career): https://soberadventuring.com/method/
- About Alexis: https://soberadventuring.com/story/

Output ONLY valid JSON — no markdown fences, no extra text. Use this exact structure:
{
  "title": "SEO title, under 60 chars, includes keyword",
  "meta_description": "155-160 chars, includes keyword, compelling",
  "slug": "url-slug-with-hyphens",
  "reading_time": 5,
  "intro": "2-3 sentence hook. Pull the reader in immediately.",
  "sections": [
    {"heading": "H2 heading", "paragraphs": ["paragraph 1", "paragraph 2", "paragraph 3"]}
  ],
  "conclusion": "2-3 sentences. Soft CTA — relevant internal link."
}

Requirements:
- 3-5 sections
- Total ~1000 words across intro + sections + conclusion
- Include keyword naturally in intro and one heading
- Each section: 2-4 substantive paragraphs, no filler
- Write as Alexis, first person, from lived experience"""


def get_topic():
    day = date.today().timetuple().tm_yday
    return TOPICS[day % len(TOPICS)]


def call_claude(topic):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Write a blog post targeting: \"{topic['keyword']}\". Category: {topic['category']}."
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
    print(f"Generating post for: {topic['keyword']}")

    data = call_claude(topic)
    print(f"Title: {data['title']}")
    print(f"Slug: {data['slug']}")

    today = date.today()
    post_date_str = today.strftime("%B %d, %Y")
    post_date_iso = today.isoformat()
    slug = data["slug"]

    # Write post HTML
    post_dir = Path(f"blog/{slug}")
    post_dir.mkdir(parents=True, exist_ok=True)
    post_path = post_dir / "index.html"
    post_path.write_text(render_post_html(data, topic, post_date_str), encoding="utf-8")
    print(f"Wrote: {post_path}")

    # Update posts.json
    posts_json = Path("blog/posts.json")
    posts = json.loads(posts_json.read_text()) if posts_json.exists() else []

    # Avoid duplicate slugs
    posts = [p for p in posts if p["slug"] != slug]
    posts.append({
        "slug": slug,
        "title": data["title"],
        "meta_description": data["meta_description"],
        "category": topic["category"],
        "date": post_date_iso,
        "reading_time": data["reading_time"]
    })
    posts.sort(key=lambda p: p["date"])
    posts_json.write_text(json.dumps(posts, indent=2), encoding="utf-8")

    # Regenerate blog index
    blog_index = Path("blog/index.html")
    blog_index.write_text(render_index_html(posts), encoding="utf-8")
    print(f"Updated blog index — {len(posts)} total posts")


if __name__ == "__main__":
    main()
