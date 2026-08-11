import html
import json
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import feedparser

ROOT = Path(__file__).parent.parent
SOURCES = json.loads((ROOT / "feeds.json").read_text())


def published_at(entry):
    value = entry.get("published_parsed") or entry.get("updated_parsed")
    if value:
        return datetime(*value[:6], tzinfo=timezone.utc).isoformat()
    for key in ("published", "updated"):
        try:
            return parsedate_to_datetime(entry[key]).astimezone(timezone.utc).isoformat()
        except (KeyError, TypeError, ValueError):
            continue
    return None


def plain_text(value):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html.unescape(value or ""))).strip()


articles = {}
errors = []
for source in SOURCES:
    parsed = feedparser.parse(source["feed_url"], agent="TechFeedDashboard/1.0")
    if parsed.bozo and not parsed.entries:
        errors.append(source["name"])
        continue
    for entry in parsed.entries:
        url = entry.get("link")
        if not url:
            continue
        articles.setdefault(url, {
            "title": plain_text(entry.get("title", "無題")),
            "url": url,
            "source": source["name"],
            "category": source["category"],
            "published_at": published_at(entry),
            "summary": plain_text(entry.get("summary", ""))[:500],
        })

payload = {
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "sources": SOURCES,
    "errors": errors,
    "articles": sorted(articles.values(), key=lambda article: article["published_at"] or "", reverse=True),
}
(ROOT / "public" / "articles.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(payload['articles'])} articles")
