"""Shared accessible storefront shell. Content and interactions live in matching.js."""
from pathlib import Path
import hashlib
import html


def home_intro():
    return '''<section class="home-hero"><img class="hero-photograph" src="/shop/images/harvest-hero.webp" alt="畑で収穫した野菜を表したイメージ" width="1536" height="1024" fetchpriority="high"><div class="hero-shade"></div><div class="hero-copy"><p class="eyebrow">生産者と、いい出会いを。</p><h1>食べたいものから、<br>つくる人と<br>つながろう。</h1><p>家庭のお取り寄せも、お店の仕入れも。<br>品目や取引の希望から、相談先を探せます。</p><a class="hero-link" href="/match/">希望条件を整理して探す</a></div><span class="image-credit">AI生成のイメージ写真</span></section>
<div class="home-search-wrap"><form id="home-search" class="home-search" action="/producers/"><label class="search-purpose"><span>何に使いますか</span><select name="audience"><option value="">用途を選ぶ</option><option value="household">家庭で楽しむ</option><option value="business">お店・事業で使う</option></select></label><label class="search-keyword"><span>どんな農産物を探しますか</span><input name="q" type="search" maxlength="100" placeholder="野菜、米、農園名など"></label><button type="submit"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg>探す</button></form><p class="search-support">公式情報を比較して、相談文まで準備できます。相談は各生産者の公式窓口へ。</p></div>'''


def render(root, path, title, content, policies):
    def asset(name):
        file = Path(root) / name.lstrip('/')
        version = hashlib.sha256(file.read_bytes()).hexdigest()[:10]
        return f'{name}?v={version}'

    def nav(href, text):
        current = ' aria-current="page"' if '/' + path == href else ''
        return f'<a href="{href}"{current}>{text}</a>'

    leaf = '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M25 5C10 3 3 13 8 22c9 5 19-2 17-17Z"/><path d="m7 26 14-14M13 20l-1-7m1 7 7 1"/></svg>'
    shop = path.startswith(('products/', 'cart/', 'checkout/', 'complete/', 'orders/')) or path in ('producers/field/', 'producers/orchard/')
    notice = '<div class="sample-banner">購入機能の操作サンプルです。商品・生産者は架空で、注文・課金・発送はありません。</div>' if shop else ''
    robots = 'index,follow' if not path or path.rstrip('/') in policies else 'noindex,follow'
    if not path:
        content = home_intro() + '<section class="home-section"><h2>生産者の公式情報</h2><p>条件検索・候補比較はJavaScriptを有効にしてご利用ください。</p>' + content[content.index('<ul>'):] + '</section>'
    page_attr = ' data-page="home"' if not path else ''
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{html.escape(title)}｜農産物と生産者のマッチング案内サイト</title>
<meta name="description" content="農産物を探す人と生産者をつなぐ案内サイトです。用途・数量・規格・納品頻度などの希望を整理し、公式情報を比較して相談文を作成できます。現在の受付可否は各公式窓口で確認してください。">
<meta name="theme-color" content="#203e32">
<link rel="canonical" href="https://agri.shiokonbu.com/{path}">
<meta name="robots" content="{robots}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{asset('/shop/store.css')}">
<script src="{asset('/shop/matching-core.js')}" defer></script>
<script src="{asset('/shop/matching.js')}" defer></script>
<script src="{asset('/shop/store.js')}" defer></script>
</head>
<body>
<a class="skip" href="#content">本文へ移動</a>
{notice}
<header class="site-header">
  <div class="header-inner">
    <a class="brand" href="/">{leaf}<span>産地のつながり<small>つくる人を知る。食べる楽しみが広がる。</small></span></a>
    <button class="menu-toggle icon-button" id="menu-toggle" aria-controls="site-menu" aria-expanded="false" aria-label="メニューを開く"><span></span><span></span></button>
    <nav id="site-menu" aria-label="メインナビゲーション">
      {nav('/producers/', '生産者を探す')}
      {nav('/match/', '希望条件から探す')}
      {nav('/how-it-works/', 'ご利用ガイド')}
      <a class="header-saved" href="/requests/">相談の下書き</a>
      <a class="header-producer" href="/for-producers/">生産者の方へ</a>
      <a class="header-cart" href="/cart/" aria-label="購入サンプルのカート">カート <span id="count">0</span></a>
    </nav>
  </div>
</header>
<main id="content" tabindex="-1"{page_attr}>{content}</main>
<div id="global-status" class="toast" role="status" aria-live="polite" aria-atomic="true"></div>
<footer class="site-footer">
  <div class="footer-top"><div><a class="brand footer-brand" href="/">{leaf}<span>産地のつながり</span></a><p>食べたいものから、つくる人と。<br>希望を整理し、相談先を探すお手伝い。</p></div>
    <nav aria-label="フッターナビゲーション"><div><h2>探す・相談する</h2><a href="/producers/">生産者の公式情報</a><a href="/match/">希望条件から探す</a><a href="/compare/">選んだ候補を比較</a><a href="/requests/">相談の下書き</a></div><div><h2>このサービスについて</h2><a href="/how-it-works/">ご利用ガイド</a><a href="/for-producers/">生産者の方へ</a><a href="/contact/">お問い合わせについて</a><a href="/repair/">機械修理さがし</a></div><div><h2>購入機能について</h2><a href="/products/">購入の操作サンプル</a><a href="/orders/">デモ注文の記録</a><a href="/shipping/">配送・返品・返金</a><a href="/legal/">特定商取引法に基づく表記</a></div></nav>
  </div>
  <div class="footer-bottom"><p>公式公開情報への参照です。提携・登録生産者の一覧ではありません。</p><div><a href="/terms/">利用規約</a><a href="/privacy/">プライバシー</a><button id="clear" type="button">端末の保存データを削除</button></div><p id="storage-status" role="status"></p><small>© 産地のつながり</small></div>
</footer>
<nav class="mobile-nav" aria-label="モバイルナビゲーション"><a href="/" data-mobile="home"><span aria-hidden="true">⌂</span>ホーム</a><a href="/producers/" data-mobile="search"><span aria-hidden="true">⌕</span>探す</a><a href="/compare/" data-mobile="compare"><span aria-hidden="true">▥</span>比較 <b data-selected-count>0</b></a><a href="/requests/" data-mobile="saved"><span aria-hidden="true">▤</span>下書き</a></nav>
</body></html>
'''
