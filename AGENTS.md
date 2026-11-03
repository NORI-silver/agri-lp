# AGENTS.md — 農機修理さがし（agri.shiokonbu.com）

このリポジトリで作業するすべてのAI（Claude・Codex・ほかのモデル）と人のための共通ルールです。`CLAUDE.md` はこのファイルを読み込むだけです。
オーナーは Nori さん（個人）。やりとりは日本語で、やさしく短く。編集・反映はAIが行います。

## 構想と作業の分類

- 中長期の方針は「SHIOKONBU Agri 構想 v1.0」（農機具の出張修理・メンテナンスの事業者DB＋マッチング＋送客基盤）。
- 提案・PR・作業ログでは最初に [A] 北極星／[B] 集客（SEO・SNS）／[C] 内部DB＋管理画面／[D] 実データでの検証／[E] 空き状況・マッチング・AI対応／[F] マネタイズ／[G] 並列の進め方 のどれかを書く。
- SEO・集客の方針は `docs/strategy.md`（元はClaude Doc「SHIOKONBU Agri SEO・集客戦略 v0.1」）。

## サイトの作り方

- 静的サイト（GitHub Pages）。中身は `tools/pages.py`、HTML・sitemap.xml・llms.txt は `python3 tools/build.py .` で作り直してコミットする（HTMLを直接直さない）。
- PRの前に `python3 tools/seo_check.py .` を通す（CIでも走る）。
- 事業者DBは別管理（運営内部用、非公開）。このリポジトリには、公開してよいと確認した項目だけを持ってくる。

## 書いてよいこと・書かないこと

- **サイト上に「shiokonbu」「SHIOKONBU」の名前を出さない**（Nori 2026-11-03）。画面・タイトル・メタ情報・構造化データ・llms.txt のサイト名は「農機修理さがし」。ドメイン（agri.shiokonbu.com）はそのまま。`seo_check.py` で止める。社内の呼び名「SHIOKONBU Agri 構想」はリポジトリの文書の中だけで使う。

- 書いてよいのは、公式サイト・公式の料金表・事業者への確認で分かったことだけ。数字には出典（`SOURCES`）と確認日を付ける。
- 確かめていない項目は「未確認」と書く。空いている・対応できるように見せない。
- 根拠のない売り文句（「24時間」「即日対応」「最短30分」「No.1」など）は書かない（`seo_check.py` の BAN で止める）。
- 事業者の並びに順位はつけない。
- **症状ページ（「エンジンがかからない」など、自分で確かめる手順を書くページ）は、整備士の監修を取れるまで公開しない**（けが・故障の広がりにつながるため）。
- **薄いページを作らない**：市町村ページは確認済みの事業者が3社以上、県のページは10社以上になってから公開する。事業者ごとのページは本人の確認まで noindex。
- 事業者に連絡する（電話・メール）ことは、Nori さんの方針に従う。

## 計測

- `ga.js` の GA4 で、本番だけ計測する。送り先は2つ：shiokonbu.com 総合（G-ZYX17VBTWB、プロパティ 292677591。全サブドメイン共通、消さない）と agri 単体（G-QXP10ZVT9S、SHIOKONBU アカウントの agri.shiokonbu.com プロパティ）。電話（tel:）・LINE・`data-inquiry` 付きリンクのクリックをイベントで数える（KPIは「問い合わせ行動」。PVではない）。

## Nori さんの操作が必要なこと（2026-11-03時点）

1. DNS：`agri.shiokonbu.com` の CNAME を `nori-silver.github.io` に向ける。
2. GitHub：Settings → Pages → Source を「GitHub Actions」にし、Custom domain に `agri.shiokonbu.com`、Enforce HTTPS をオン。
3. Search Console に `agri.shiokonbu.com` を追加し、sitemap.xml を送る。
4. ~~GA4~~ 済み（2026-11-03、プロパティ agri.shiokonbu.com・測定ID G-QXP10ZVT9S）。
