"""
One-time script: rewrite all existing blog posts using the updated system prompt
and claude-sonnet-4-6. Preserves original slug, date, and category for each post.
Triggered manually via GitHub Actions (rewrite-all-posts.yml).
"""
import anthropic
import os
import json
import re
from datetime import date
from pathlib import Path

from generate_post import SYSTEM_PROMPT, TOPICS, render_post_html, render_index_html

CLIENT = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
MODEL = "claude-sonnet-4-6"

# Build a lookup: normalized title -> topic (for keyword retrieval)
TOPIC_BY_TITLE = {t["title"].lower(): t for t in TOPICS}


def find_keyword(title, category):
    title_lower = title.lower()
    if title_lower in TOPIC_BY_TITLE:
        return TOPIC_BY_TITLE[title_lower]["keyword"]
    # Fuzzy: find topic in same category with most word overlap
    best_overlap, best_kw = 0, ""
    post_words = set(title_lower.split())
    for t in TOPICS:
        if t["category"] != category:
            continue
        overlap = len(set(t["title"].lower().split()) & post_words)
        if overlap > best_overlap:
            best_overlap, best_kw = overlap, t["keyword"]
    return best_kw


def call_claude(title, keyword, category):
    msg = CLIENT.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": (
                f"Write a blog post with this title: \"{title}\"\n"
                f"Target keyword(s): {keyword}\n"
                f"Category: {category}\n\n"
                "Remember: value first. This must be a genuinely useful resource. "
                "Research-based where possible. Specific and actionable. "
                "Alexis's voice and experience as texture, not the main substance. "
                "No em dashes. No short standalone sentences. Full flowing prose. "
                "No 'Not because X. But because Y.' or any fragment-pair structures. "
                "No triads: never list three things, pick the two strongest and cut the third. "
                "Hedge all claims about what people experience or feel: might, may, often. Never 'you will' or 'everyone.' "
                "Use <strong>, <u>, and <span class=\"hl\"> sparingly where they genuinely help the reader scan, not for decoration."
            )
        }]
    )
    text = msg.content[0].text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    if text.lower().startswith("json"):
        text = text[4:]
    return json.loads(text.strip())


def main():
    posts_json = Path("blog/posts.json")
    posts = json.loads(posts_json.read_text())
    print(f"Rewriting {len(posts)} posts with Sonnet + full writing rules...\n")

    updated_posts = []
    for i, post in enumerate(posts, 1):
        slug = post["slug"]
        title = post["title"]
        category = post["category"]
        post_date = post["date"]
        reading_time = post.get("reading_time", 7)

        keyword = find_keyword(title, category)
        print(f"[{i}/{len(posts)}] {title}")

        try:
            data = call_claude(title, keyword, category)

            # Lock slug and date — only content changes
            data["slug"] = slug

            post_date_str = date.fromisoformat(post_date).strftime("%B %d, %Y")
            topic_obj = {"category": category}

            post_dir = Path(f"blog/{slug}")
            post_dir.mkdir(parents=True, exist_ok=True)
            (post_dir / "index.html").write_text(
                render_post_html(data, topic_obj, post_date_str), encoding="utf-8"
            )

            updated_posts.append({
                "slug": slug,
                "title": data["title"],
                "meta_description": data["meta_description"],
                "category": category,
                "date": post_date,
                "reading_time": data.get("reading_time", reading_time),
            })
            print(f"  OK")

        except Exception as e:
            print(f"  ERROR: {e} — keeping original")
            updated_posts.append(post)

    updated_posts.sort(key=lambda p: p["date"])
    posts_json.write_text(json.dumps(updated_posts, indent=2), encoding="utf-8")

    Path("blog/index.html").write_text(render_index_html(updated_posts), encoding="utf-8")
    print(f"\nDone. {len(updated_posts)} posts processed.")


if __name__ == "__main__":
    main()
