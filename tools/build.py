#!/usr/bin/env python3
"""農機修理さがし（agri.shiokonbu.com）の静的ページを作る（外部ライブラリ不要）。
使い方: python3 tools/build.py .
中身は tools/pages.py。生成した HTML・sitemap.xml・llms.txt もコミットする。
"""
import html, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pages as P  # noqa: E402

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
SITE = "https://agri.shiokonbu.com"
NAME = "農機修理さがし"  # サイト上に「shiokonbu」は出さない（Nori 2026-11-03）
TODAY = "2026-11-03"

LOGO = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M5 17a3 3 0 1 0 0 .01zM18 15a4 4 0 1 0 0 .01zM4 13V8h6l2 4h4V7h2v5.2A5 5 0 0 0 13.6 15H8.9A3.5 3.5 0 0 0 4 13z"/></svg>'


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
        body.append(f'<section><h2>{html.escape(h2)}</h2>{fill(content, used)}</section>')
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
            f'<li id="src-{k}"><a href="{P.SOURCES[k][1]}" rel="nofollow noopener" target="_blank">{html.escape(P.SOURCES[k][0])}</a></li>'
            for k in used) + f"</ol><p>{TODAY}に確認。</p></section>")
    if path:
        rel = [(f"/machine/{s}/", n) for s, n in P.MACHINES] + [(f"/guide/{s}/", n) for s, n in P.GUIDES]
        rel = [(h, n) for h, n in rel if h != "/" + path]
        body.append('<nav class="related" aria-label="ほかのページ"><h2>ほかのページ</h2><ul>' + "".join(
            f'<li><a href="{h}">{html.escape(n)}</a></li>' for h, n in rel) + "</ul></nav>")
    crumb_html = "" if not path else f'<nav class="crumb" aria-label="パンくず"><a href="/">トップ</a> › {html.escape(label(path))}</nav>'
    t, desc = html.escape(d["title"]), html.escape(d["desc"])
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
<header class="top"><div class="wrap">
<a class="logo" href="/"><i>{LOGO}</i>{NAME}</a>
<nav><a href="/#machine">機種</a><a href="/#guide">困りごと</a><a href="/guide/fee/">費用</a><a href="/about/">このサイトについて</a></nav>
</div></header>
<main class="wrap">
{crumb_html}
<h1>{html.escape(d['h1'])}</h1>
<p class="lead">{html.escape(d['lead'])}</p>
{''.join(body)}
</main>
<footer><div class="wrap"><p><a href="/">{NAME}</a>｜農機が壊れたときの頼み先さがし</p><p><a href="/about/">このサイトについて</a></p></div></footer>
</body>
</html>
"""


def main():
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
             "> 農機（トラクター・コンバイン・田植機・草刈機など）が壊れたときに、どこに頼めるか、来てもらえるか、そのメーカー・機種に対応できるかを探せるようにするサイトです。修理の頼み方・費用の目安・農繁期の備えをまとめています。地域ごとの事業者の一覧は千葉県から準備中です。",
             "", "- 載せているのは、公式サイト・公式の料金表・事業者への確認で分かったことだけです。", "",
             "## 機種"] + [f"- [{n}の修理の頼み方]({SITE}/machine/{s}/)" for s, n in P.MACHINES] + ["", "## 困りごと"] + \
            [f"- [{n}]({SITE}/guide/{s}/)" for s, n in P.GUIDES] + ["", f"- [このサイトについて]({SITE}/about/)", ""]
    open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8").write("\n".join(lines))


if __name__ == "__main__":
    main()
