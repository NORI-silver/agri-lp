# [A] 農産物マーケット実装と公開範囲（2026-11-23）

## 運用の境界

公開先はGitHub Pages。公開版は架空商品4件・架空生産者2件の操作デモ。実注文・課金・発送・個人情報収集は開始しない。許諾済みの商品データは未取得。修理DBは非公開のまま利用せず、既存修理コンテンツのURLは保持し、旧トップだけ `/repair/` に移す。ルートURLは新トップと共用できないため旧トップへの301は設定しない。既存の個別記事は移転させない。検索流入・順位への影響は公開後にSearch Consoleで観測が必要で、維持を保証しない。

## 構成

- `tools/store.py`：商品・生産者デモデータ、ストアHTML生成。写真の代わりにデモと明示した自作SVG。
- `shop/store.js`：検索、カテゴリー・産地・旬・在庫絞り込み、価格順、商品/生産者詳細、カート、数量・在庫検証、送料、確認、デモ完了、端末記録削除。
- `shop/runtime.json`：公開版は `orderEndpoint: null`。記録はlocalStorageのみ。運営者は収集しない。端末をまたぐ共有・在庫引当は行わない。端末内の連打を防止するが実ECの注文保証には使用しない。
- `server/app.py`：**ローカルテスト専用**、Python標準ライブラリとSQLite。`AGRI_DB=/tmp/agri-demo.sqlite AGRI_ADMIN_TOKEN=<local-secret> python3 server/app.py`。127.0.0.1:8874で動作。ランタイム設定を上書きし、同じ画面からPOST `/api/orders`へ接続。価格・送料はサーバーで再計算、注文保存と在庫減算は同一トランザクション。注文識別子と内容による冪等性、同時注文時の在庫超過防止、失敗時ロールバック。管理用GET `/api/admin/orders` は環境変数のBearerトークン必須。個人情報は受け付けない。インターネット公開用の運用基盤・認証・監視・バックアップは未整備。
- 公開ワークフローは公開用ファイルだけステージし、server/tools/docs/.gitを配信しない。
- 法務ページは未確定条件と販売停止状態を明記。実販売に必要な正式表記の完成ではない。お問い合わせ受付先は未設定。

## 決済・実販売の残り

Stripeはアカウント・テストキー未提供のため未接続。シミュレーション成功を決済成功とは扱わない。販売主体・口座・手数料負担・配送責任・返金方針・商品掲載許諾の確定後、Stripe Checkout（カード情報を自前で持たない）と署名検証付きwebhookを接続する。販売者ごとに決済するか、マーケットプレイスが受領するかで契約構成が異なるため、Connectの契約や有料インフラを勝手に作らない。実運用向けの認証・受注管理・在庫同期・返金・通知・監査ログも未完成。現段階を実販売可能なEC完成と報告しない。

## 検証

`python3 tools/build.py .` / `python3 tools/seo_check.py .` / `python3 -m unittest discover -s tools/tests -p 'test_*.py' -v` / `node --check shop/store.js`

ブラウザー検証：Playwright 1.65.1を作業外の一時ディレクトリに入れ、`PLAYWRIGHT_MODULE=<path>/node_modules/playwright node tools/tests/store-browser.cjs` と `store-api-browser.cjs` を実行。ChromeはmacOSの既存ChromeまたはCIの `/usr/bin/google-chrome`（`CHROME_PATH`）。390pxで検索、0件、数量不正、在庫切れ、数量保持、削除、北海道送料、必須項目、連打、完了後再読込、修理表示、端末データ削除を確認。API版はSQLite保存・在庫減算・管理認証・異なるOrigin拒否・内部ファイル非公開を確認。DB単体5テストで冪等性、内容改変拒否、不正入力、在庫競合、ロールバックを確認。
