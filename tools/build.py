#!/usr/bin/env python3
"""機械修理さがし（agri.shiokonbu.com）の静的ページを作る（外部ライブラリ不要）。
使い方: python3 tools/build.py .
中身は tools/pages.py。生成した HTML・sitemap.xml・llms.txt もコミットする。
"""
import html, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pages as P  # noqa: E402

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
SITE = "https://agri.shiokonbu.com"
NAME = "機械修理さがし"  # サイト上に「shiokonbu」は出さない（Nori 2026-11-03）
TODAY = "2026-11-03"

LOGO = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14.5 6.5a5 5 0 0 0-6.8 6.8L3 18a2.1 2.1 0 0 0 3 3l4.7-4.7a5 5 0 0 0 6.8-6.8L14 13l-3-3z"/></svg>'


def label(path):
    for slug, name in P.MACHINES:
        if path == f"machine/{slug}/":
            return name
    for slug, name in P.GUIDES:
        if path == f"guide/{slug}/":
            return name
    return {"about/": "このサイトについて"}.get(path, "")


def cards(items, prefix):
    out = ['<div class="cards">']
    for slug, name in items:
        out.append(f'<a class="card" href="/{prefix}/{slug}/">{html.escape(name)}<span aria-hidden="true">›</span></a>')
    out.append("</div>")
    return "".join(out)


def fill(text, used):
    s = P.DB_STATS
    text = text.replace("{machine_cards}", cards(P.MACHINES, "machine"))
    text = text.replace("{guide_cards}", cards(P.GUIDES, "guide"))
    text = text.replace("{agri_cards}", cards([(s, n) for s, n in P.MACHINES if s != "mower"], "machine"))
    text = text.format_map({"total": s["total"], "onsite_stated": s["onsite_stated"],
                            "fee_public": s["fee_public"], "as_of": s["as_of"]}) if "{total}" in text else text
    for k, v in (("db_total", s["total"]), ("db_fee_public", s["fee_public"]), ("db_as_of", s["as_of"])):
        text = text.replace("{" + k + "}", str(v))

    def src(m):
        key = m.group(1)
        if key not in used:
            used.append(key)
        return f'<a href="#src-{key}">[{used.index(key) + 1}]</a>'
    return re.sub(r"\{src:([a-z0-9-]+)\}", src, text)


def page(path, d):
    url = SITE + "/" + path
    used = []
    body = []
    for h2, content in d["sections"]:
        anchor = {"どんな機械でお困りですか": "machine", "修理を頼む前に読むガイド": "guide", "持ち込みできないときは": "transport"}.get(h2)
        attr = f' id="{anchor}"' if anchor else ""
        body.append(f'<section{attr}><h2>{html.escape(h2)}</h2>{fill(content, used)}</section>')
    ld = []
    crumbs = [{"@type": "ListItem", "position": 1, "name": NAME, "item": SITE + "/"}]
    if path:
        crumbs.append({"@type": "ListItem", "position": 2, "name": label(path), "item": url})
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": crumbs})
    else:
        ld.append({"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": SITE + "/", "inLanguage": "ja"})
    if d.get("faq"):
        body.append("<section><h2>よくある質問</h2>" + "".join(
            f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>" for q, a in d["faq"]) + "</section>")
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in d["faq"]]})
    if used:
        body.append('<section class="sources"><h2>出典</h2><ol>' + "".join(
            f'<li id="src-{k}"><a href="{P.SOURCES[k][1]}" rel="noopener" target="_blank">{html.escape(P.SOURCES[k][0])}</a>（確認日：{P.SOURCES[k][2]}）</li>'
            for k in used) + "</ol></section>")
    if path:
        rel = [(f"/machine/{s}/", n) for s, n in P.MACHINES] + [(f"/guide/{s}/", n) for s, n in P.GUIDES]
        rel = [(h, n) for h, n in rel if h != "/" + path]
        body.append('<nav class="related" aria-label="ほかのページ"><h2>ほかのページ</h2><ul>' + "".join(
            f'<li><a href="{h}">{html.escape(n)}</a></li>' for h, n in rel) + "</ul></nav>")
    crumb_html = "" if not path else f'<nav class="crumb" aria-label="パンくず"><a href="/">トップ</a> › {html.escape(label(path))}</nav>'
    t, desc = html.escape(d["title"]), html.escape(d["desc"])
    hero = ' class="hero"' if d.get("hero") else ' class="page-intro"'
    actions = '<div class="actions"><a class="button" href="/machine/mower/">草刈機の修理相談</a><a class="button secondary" href="/guide/other-store/">購入店に頼めないとき</a></div>' if d.get("hero") else ''
    next_step = '' if not path else '<aside class="next-step"><div><span class="eyebrow">次の一歩</span><h2>機械と条件をまとめて、相談先へ。</h2><p>購入経路と持込・出張の希望も伝え、受付できるかを確認しましょう。</p></div><div class="actions"><a class="button" href="/guide/maker/">メーカーの公式案内へ</a><a class="button secondary" href="/guide/how-to-ask/">相談の準備を見る</a></div></aside>'

    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{t}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{'website' if not path else 'article'}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="{NAME}">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#2f6b2f">
<meta name="google-site-verification" content="MmM3OGz9LIPxBOmE4jR8GdP4vACP_FrchZwBLT3W0sM">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/style.css">
<script src="/ga.js"></script>
<script type="application/ld+json">
{json.dumps(ld if len(ld) > 1 else ld[0], ensure_ascii=False, indent=1)}
</script>
</head>
<body>
<a class="skip" href="#content">本文へ移動</a>
<header class="top"><div class="wrap">
<a class="logo" href="/"><i>{LOGO}</i>{NAME}</a>
<nav aria-label="メインナビゲーション"><a href="/#machine">機械から探す</a><a href="/guide/other-store/">購入店に頼めない</a><a href="/guide/how-to-ask/#transport">持込・出張</a><a href="/guide/fee/">費用</a><a href="/about/">掲載方針</a></nav>
</div></header>
<main class="wrap" id="content">
{crumb_html}
<div{hero}>
<p class="eyebrow">小型機械・作業機・農業機械の修理相談ガイド</p>
<h1>{html.escape(d['h1']).replace(chr(10), '<br>')}</h1>
<p class="lead">{html.escape(d['lead'])}</p>
{actions}
</div>
{''.join(body)}
{next_step}
</main>
<footer><div class="wrap"><p><a href="/">{NAME}</a>｜購入店に頼めない機械の修理相談に</p><p>草刈機・作業機から農業機械まで。条件別の修理先一覧・修理受付は準備中です。</p><p><a href="/about/">掲載方針・現在のサービス範囲</a> ／ <a href="/guide/maker/">メーカーの公式案内</a></p></div></footer>
</body>
</html>
"""


def main():
    not_found = f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex"><title>ページが見つかりません｜{NAME}</title><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css"></head>
<body><main class="wrap page-intro"><p class="eyebrow">{NAME}</p><h1>ページが見つかりません</h1><p>アドレスが変わったか、公開されていないページです。</p><div class="actions"><a class="button" href="/">トップへ戻る</a><a class="button secondary" href="/guide/how-to-ask/">修理相談の準備へ</a></div></main></body></html>
"""
    open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8").write(not_found)
    paths = list(P.PAGES)
    for path in paths:
        out = os.path.join(ROOT, path, "index.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        html_text = page(path, P.PAGES[path])
        if not path:  # トップの見出しにアンカーをつける
            html_text = html_text.replace("<section><h2>機種から探す", '<section id="machine"><h2>機種から探す')
            html_text = html_text.replace("<section><h2>困りごとから探す", '<section id="guide"><h2>困りごとから探す')
        open(out, "w", encoding="utf-8").write(html_text)
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for path in paths:
            f.write(f"  <url><loc>{SITE}/{path}</loc><lastmod>{TODAY}</lastmod></url>\n")
        f.write("</urlset>\n")
    lines = [f"# {NAME}", "",
             "> 購入店不明・他店やネット購入・持込困難な小型機械・作業機・農業機械の修理相談ガイド。草刈機・刈払機から、条件の確認できる修理先への接続を目指しています。",
             "", "- 現在利用できるのは相談準備のガイドとメーカー公式案内へのリンクです。条件別業者検索・修理受付・仲介・空き状況照会は準備中です。",
             "- 千葉県の草刈機・刈払機から供給条件の確認を進める方針です。未確認の受付可否は保証しません。",
             "- 農業機械は継続対象です。農機の料金例を他カテゴリや地域の相場に流用しません。",
             "", "## 機械"] + [f"- [{n}の修理相談]({SITE}/machine/{s}/)" for s, n in P.MACHINES] + ["", "## 相談ガイド"] + \
            [f"- [{n}]({SITE}/guide/{s}/)" for s, n in P.GUIDES] + ["", f"- [掲載方針・サービス範囲]({SITE}/about/)", ""]
    open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8").write("\n".join(lines))


if __name__ == "__main__":
    main()
