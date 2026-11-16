# Tech Feed

GitHub Pagesで公開する静的な技術情報ダッシュボードです。GitHub ActionsがRSSを取得して`public/articles.json`を生成し、画面はそのJSONを表示します。保存機能やユーザー認証はありません。

## 収集元

Speaker Deck、はてなブックマーク IT、DevelopersIO（AWS・Claude・Azureタグ）、Qiita・Zenn（AWS・Azure・Claude・ChatGPT・Kubernetes・Dockerタグ）を収集します。

## GitHub Pagesへの公開

1. このフォルダをGitHubリポジトリとしてpushします。
2. リポジトリの **Settings → Pages → Build and deployment** で **GitHub Actions** を選びます。
3. `pages.yml` がpush時と約30分ごとにRSSを取得し、GitHub Pagesへデプロイします。

## Slackへの毎日通知

毎日10:00（日本時間）に、前日0:00〜23:59の新着をカテゴリ別にSlackへ投稿します。リポジトリの **Settings → Secrets and variables → Actions** で、`SLACK_WEBHOOK_URL` にIncoming Webhook URLを登録してください。

Webhook未設定の場合、Slack投稿はスキップされます。

## セキュリティ上の注意

GitHub Pagesではレスポンスヘッダを設定できないため、iframe埋め込み（クリックジャッキング）は防げません。認証や保存機能がないため影響は限定的です。Docker配信ではnginxが`X-Frame-Options`とCSPヘッダで埋め込みを禁止します。

## ローカル確認

```bash
python -m pip install -r requirements.txt
python scripts/fetch_feeds.py
docker compose up -d --build
```

ブラウザで [http://localhost:8088](http://localhost:8088) を開いてください。
