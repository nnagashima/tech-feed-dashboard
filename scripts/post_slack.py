import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen

def esc(value):
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


JST = timezone(timedelta(hours=9))
webhook = os.environ.get("SLACK_WEBHOOK_URL")
if not webhook:
    raise SystemExit("SLACK_WEBHOOK_URL is not configured")

data = json.loads((Path(__file__).parent.parent / "public" / "articles.json").read_text())
yesterday = datetime.now(JST).date() - timedelta(days=1)
grouped = {}
for article in data["articles"]:
    if not article["published_at"] or not article["url"].lower().startswith(("http://", "https://")):
        continue
    if datetime.fromisoformat(article["published_at"]).astimezone(JST).date() == yesterday:
        grouped.setdefault(article["category"], []).append(article)

blocks = [{"type": "header", "text": {"type": "plain_text", "text": f"Tech Feed｜{yesterday:%Y/%m/%d} の新着"}}]
if not grouped:
    blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "前日の新着記事はありませんでした。"}})
else:
    total = sum(map(len, grouped.values()))
    blocks.append({"type": "context", "elements": [{"type": "mrkdwn", "text": f"*{total}件* の新着を収集しました"}]})
    for category, articles in grouped.items():
        lines = [f"*{category}*"] + [f"• <{esc(a['url'])}|{esc(a['title'])}>  _{esc(a['source'])}_" for a in articles[:5]]
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "\n".join(lines)}})

request = Request(webhook, data=json.dumps({"blocks": blocks}, ensure_ascii=False).encode(), headers={"Content-Type": "application/json"}, method="POST")
with urlopen(request, timeout=15) as response:
    if not 200 <= response.status < 300:
        raise RuntimeError(f"Slack returned HTTP {response.status}")
