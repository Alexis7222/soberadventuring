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
    {"title": "What Is Marijuana-Induced Psychosis and Who Is at Risk",             "keyword": "marijuana induced psychosis cannabis psychosis",               "category": "Recovery"},
    # Sobriety Coaching
    {"title": "What Does a Sobriety Coach Actually Do? (It's Not Therapy)",         "keyword": "sobriety coach what is sobriety coaching",                     "category": "Sobriety Coaching"},
    {"title": "Sobriety Coach vs. Therapist vs. AA: Which Support Is Right for You?", "keyword": "sobriety coach vs therapy alternatives to AA",             "category": "Sobriety Coaching"},
    {"title": "How Much Does a Sober Coach Cost? Breaking Down the Investment",     "keyword": "sobriety coach cost sober coach online",                       "category": "Sobriety Coaching"},
    {"title": "5 Signs You Might Benefit From a Sobriety Coach",                    "keyword": "sobriety coaching alcohol free coaching",                      "category": "Sobriety Coaching"},
    {"title": "Can You Get Sober Online? What Remote Sobriety Coaching Looks Like", "keyword": "online sobriety support sober coach online",                   "category": "Sobriety Coaching"},
    {"title": "The ALIVE Method: A Non-12-Step Framework for Sobriety Coaching",    "keyword": "sobriety coaching sobriety framework ALIVE method",            "category": "Sobriety Coaching"},
    {"title": "How to Build a Sober Life You Actually Want to Live",                "keyword": "sobriety coach sober accountability coach",                    "category": "Sobriety Coaching"},
    # Sober Travel
    {"title": "The Complete Guide to Sober Travel: How to Have the Best Trip",      "keyword": "sober travel sober travel tips",                               "category": "Sober Travel"},
    {"title": "Sober in Chiang Mai: A Digital Nomad's Guide Without Alcohol",       "keyword": "sober in Thailand sober travel digital nomad",                 "category": "Sober Travel"},
    {"title": "How to Handle Social Drinking While Traveling (Without Caving)",     "keyword": "how to travel sober sober travel tips",                        "category": "Sober Travel"},
    {"title": "The Best Destinations for Sober Travel in Southeast Asia",           "keyword": "sober travel alcohol free vacation Southeast Asia",             "category": "Sober Travel"},
    {"title": "Dry Tripping: What It Is and Why Gen Z Is Leading This Revolution",  "keyword": "dry tripping sober travel trend",                              "category": "Sober Travel"},
    {"title": "Can You Be a Digital Nomad and Stay Sober?",                         "keyword": "digital nomad sober traveling in recovery",                    "category": "Sober Travel"},
    {"title": "What Happened When I Traveled to Multiple Countries Sober",          "keyword": "sober travel blog traveling in recovery honest",               "category": "Sober Travel"},
    # Non-12-Step / Secular
    {"title": "Can You Get Sober Without AA? Yes, and Here's What That Looks Like", "keyword": "sobriety without AA alternatives to AA",                       "category": "Recovery"},
    {"title": "Non-12-Step Recovery: Every Alternative Explained",                  "keyword": "non 12 step recovery alternatives to AA SMART LifeRing",       "category": "Recovery"},
    {"title": "How to Get Sober If You're Not Religious",                           "keyword": "non religious sobriety secular sobriety no higher power",      "category": "Recovery"},
    {"title": "SMART Recovery vs. AA: An Honest Comparison",                        "keyword": "SMART recovery non 12 step recovery vs AA",                    "category": "Recovery"},
    {"title": "Why Diversifying Your Recovery Modalities Matters",                  "keyword": "secular sobriety non religious sobriety recovery community",    "category": "Recovery"},
    {"title": "The Problem With Relying on One Recovery Program",                   "keyword": "alternatives to AA non religious sobriety",                    "category": "Recovery"},
    # Freelance / Lifestyle
    {"title": "How to Build a Freelance Business While in Recovery",                "keyword": "sober freelance sobriety lifestyle career change Upwork",      "category": "Freelance"},
    {"title": "Why Getting Sober Was the Best Career Move I Ever Made",             "keyword": "sobriety benefits sober lifestyle career sobriety tips",       "category": "Freelance"},
    {"title": "How to Start Freelancing on Upwork With No Experience",              "keyword": "how to start freelancing on Upwork with no experience",        "category": "Freelance"},
    {"title": "How to Write Upwork Proposals That Actually Get Responses",          "keyword": "Upwork proposals how to get clients on Upwork",                "category": "Freelance"},
]

SYSTEM_PROMPT = """You write blog posts for soberadventuring.com — Alexis Antonelli's site.

== ABOUT ALEXIS (FACTS ONLY — DO NOT FABRICATE DETAILS) ==
- Got sober again at 24 after a second marijuana-induced psychosis. Started trying at 18. Previous stints: 2 years, 9 months, 6 months, 5 months.
- Uses the 12 steps as one tool among several. Also has experience with Refuge Recovery, SMART Recovery. Has a sponsor.
- Believes recovery modalities should be diversified, the same way a financial portfolio should be. The 12 steps can become its own dependency for some people.
- 4 years working in rehab and mental health spaces: recovery support specialist, sober house manager, ABA therapist (children and teenagers with autism and developmental delays), ran recovery groups, case management.
- First job ever was in sales. Had cold calling and closing experience. Addiction scattered the resume.
- Went to Upwork, started with cold calling contracts, progressed to closing roles, consulting, outbound pipeline architecture, training SDRs, writing sales playbooks, CRM migration, working directly with founders and CEOs.
- Made $30k in first 4 months on Upwork.
- Now runs Impello Agency (sales agency, 13+ case studies) and coaches people through the PIVOT Method (career) and ALIVE Method (sobriety). Based in Chiang Mai, Thailand.
- Not a licensed therapist.

== ARTICLE PHILOSOPHY — THIS IS THE MOST IMPORTANT INSTRUCTION ==
Articles must be VALUE FIRST. The primary goal is to be a useful, trustworthy resource for the reader. Think of each post as something a person in a hard moment could find through Google and walk away from with real, actionable information.

- Lead with what the reader needs to know, not with Alexis's personal story.
- Use research, data, and established frameworks where they exist. Cite specific facts when relevant (e.g., "studies show," "according to," specific statistics).
- Personal perspective and experience from Alexis can be woven in, but sparingly — as credibility and texture, not as the main substance.
- The reader should finish the article better equipped than when they started. That is the only metric that matters.
- Do not write content that is primarily self-promotional or that reads like a personal essay. The story page exists for that.

== VOICE AND TONE ==
- Direct and clear. No unnecessary complexity.
- Warm but not soft. This is not a wellness blog. It is a resource site.
- Honest about what is hard, what is uncertain, and what varies person to person.
- First person is fine where genuinely relevant. Do not force it.
- No preaching, no moralizing, no inspirational padding.

== WRITING RULES — ALL NON-NEGOTIABLE ==
- Write complete, connected sentences. Paragraphs should flow as prose, not as lists of bullet points in disguise.
- No short standalone sentences used for dramatic effect.
- No rapid-fire imperative sentences: never write "Do X. Do Y. Do Z." as separate short sentences. Combine them into flowing prose.
- No em dashes anywhere. Rewrite the sentence instead.
- No "Not by X. By Y." or "Not X. But Y." fragment structures.
- No filler. Every sentence must earn its place.
- No moralizing or lecturing. State facts and experience, not judgments.

== BANNED PHRASES ==
em dashes (the character), delve into, delve deeper, it's important to note, in conclusion, to summarize, furthermore, moreover, additionally (as opener), navigate (metaphorically), game-changer, transformative, journey (recovery journey / freelance journey), tapestry, in today's world, let's explore, holistic approach, leverage (as verb), multifaceted, in essence, it goes without saying, needless to say, I cannot stress enough, at the end of the day, when it comes to, it's worth noting, comprehensive, robust, paramount, seamlessly, beacon, foster (as in foster growth), pivotal, embark on, realm, testament to, underscores the importance, unpack, dive into, circle back, moving forward, the bottom line is, with that said, without further ado, having said that, it's crucial that, one thing to keep in mind

== STRUCTURE ==
intro: 2-3 sentences. State clearly what the article covers and why it matters. No throat-clearing.
sections: 3-5 H2 sections of flowing prose paragraphs. Each paragraph 3-5 sentences. Substantive and specific.
conclusion: 2-3 sentences. What the reader should do next. Soft CTA with internal link as HTML <a href="URL">text</a>.
Total: ~1000-1200 words. Include target keyword naturally in first 100 words and one H2.

== INTERNAL LINKS — use where genuinely relevant ==
Free clarity call: https://calendly.com/alexis-m-antonelli/freediscoverycall
Telegram recovery group: https://t.me/+wJbhwv2ccS1hMjFh
Upwork Starter Guide ($14.99): https://antonelli74.gumroad.com/l/wfbmpv
The PIVOT Method: https://soberadventuring.com/method/
About Alexis: https://soberadventuring.com/story/

Output ONLY valid JSON, no markdown fences, no extra text:
{
  "title": "SEO title under 60 chars, includes keyword",
  "meta_description": "155-160 chars, includes keyword, sounds human",
  "slug": "url-slug-with-hyphens",
  "reading_time": 6,
  "intro": "2-3 sentence intro stating what the article covers and why it matters.",
  "sections": [
    {"heading": "H2 text", "paragraphs": ["paragraph 1", "paragraph 2", "paragraph 3"]}
  ],
  "conclusion": "2-3 sentences. What to do next. Soft CTA with HTML <a href='URL'>anchor text</a>."
}"""


def get_topic(existing_slugs):
    day = date.today().timetuple().tm_yday
    for i in range(len(TOPICS)):
        topic = TOPICS[(day + i) % len(TOPICS)]
        candidate_slug = re.sub(r"[^a-z0-9]+", "-", topic["title"].lower()).strip("-")
        if candidate_slug not in existing_slugs:
            return topic
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
                "Remember: value first. This must be a genuinely useful resource. "
                "Research-based where possible. Specific and actionable. "
                "Alexis's voice and experience as texture, not the main substance. "
                "No em dashes. No short standalone sentences. Full flowing prose."
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
<meta name="description" content="Recovery, freelancing, and sober living — practical, research-backed articles from Alexis at Sober Adventuring.">
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
  <h1>Practical.<br><em>No fluff.</em></h1>
  <p>Recovery, freelancing, and building a life worth being present for.</p>
</div>

<div class="blog-grid">
  {cards}
</div>

</body>
</html>"""


def main():
    posts_json = Path("blog/posts.json")
    posts = json.loads(posts_json.read_text()) if posts_json.exists() else []
    existing_slugs = {p["slug"] for p in posts}

    topic = get_topic(existing_slugs)
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
