#!/usr/bin/env python3
"""SEOと文言ルールの自動チェック（外部ライブラリ不要）。使い方: python3 tools/seo_check.py . → NGがあれば終了コード1。"""
import os, re, sys, collections
from html.parser import HTMLParser

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
SITE = "https://agri.shiokonbu.com"
# 確かめていないのに書きがちな言葉（AGENTS.md）。根拠があるときは出典を付けてから外す。
BAN = ["24時間", "最短30分", "業界最安", "No.1", "日本一", "即日対応", "すぐに駆けつけ", "必ず直", "実績多数"]

class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.title = ""; s.desc = None; s.canon = None; s.h1 = 0; s.h2 = 0
        s._t = False; s._skip = 0; s.text = []; s.links = []
    def handle_starttag(s, tag, a):
        a = dict(a)
        if tag == "title": s._t = True
        elif tag in ("script", "style"): s._skip += 1
        elif tag == "meta" and a.get("name") == "description": s.desc = a.get("content", "")
        elif tag == "link" and a.get("rel") == "canonical": s.canon = a.get("href")
        elif tag == "h1": s.h1 += 1
        elif tag == "h2": s.h2 += 1
        elif tag == "a" and (a.get("href") or "").startswith("/"): s.links.append(a["href"].split("#")[0])
    def handle_endtag(s, tag):
        if tag == "title": s._t = False
        elif tag in ("script", "style"): s._skip -= 1
    def handle_data(s, d):
        if s._t: s.title += d
        elif not s._skip: s.text.append(d)

def main():
    locs = re.findall(r"<loc>([^<]+)</loc>", open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read())
    ng, titles = [], collections.defaultdict(list)
    for u in locs:
        rel = u.replace(SITE, "").lstrip("/")
        f = os.path.join(ROOT, rel, "index.html")
        if not os.path.exists(f): ng.append(f"{u}: ファイルがない"); continue
        p = P(); p.feed(open(f, encoding="utf-8").read())
        titles[p.title].append(u)
        if not (20 <= len(p.title) <= 60): ng.append(f"{u}: タイトルの長さ {len(p.title)}字（20〜60）")
        if not p.desc or not (60 <= len(p.desc) <= 160): ng.append(f"{u}: ディスクリプションの長さ（60〜160）")
        if p.canon != u: ng.append(f"{u}: canonical が違う {p.canon}")
        if p.h1 != 1: ng.append(f"{u}: h1 が {p.h1}個")
        if p.h2 < 2: ng.append(f"{u}: h2 が少ない")
        text = "".join(p.text)
        raw = open(f, encoding="utf-8").read().replace("agri.shiokonbu.com", "")
        if re.search(r"shiokonbu", raw, re.I): ng.append(f"{u}: サイト上に「shiokonbu」の名前がある（ドメイン以外で使わない）")
        for w in BAN:
            if w in text: ng.append(f"{u}: 根拠のない言い方「{w}」")
        for l in p.links:
            target = os.path.join(ROOT, l.lstrip("/"), "index.html") if l.endswith("/") else os.path.join(ROOT, l.lstrip("/"))
            if not os.path.exists(target): ng.append(f"{u}: リンク切れ {l}")
    for t, us in titles.items():
        if len(us) > 1: ng.append(f"タイトルが重複: {t}")
    print("\n".join(ng) if ng else f"OK（{len(locs)}ページ）")
    sys.exit(1 if ng else 0)

main()
