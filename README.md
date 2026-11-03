# 機械修理さがし

購入店不明・他店やネット購入・持込困難な小型機械／作業機の修理相談ガイド。農業機械も対象に残し、千葉県×草刈機・刈払機から条件確認済みの修理先への接続を目指します。

現在は静的ガイドとメーカー公式案内へのリンクです。条件検索・修理受付・マッチングは未実装です。共通ルールは [AGENTS.md](AGENTS.md)、転換設計は [docs/strategy.md](docs/strategy.md)。PR #8はマージ保留です。

```sh
python3 tools/build.py .      # 本文からHTML・404・sitemap・llmsを生成
python3 tools/seo_check.py .  # SEOと文言を確認
```

ドメイン・既存URL・GA4二系統・Search Console確認タグは維持。非公開DB原本は別管理です。
