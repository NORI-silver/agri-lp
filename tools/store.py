"""Explicit demo storefront. No real orders, payments or personal data collection."""
import json, os, html
PRODUCTS = [
 dict(id='carrot',name='土付きにんじん',category='野菜',region='千葉',season='冬',price=980,amount='1kg',stock=8,producer='field',emoji='🥕',color='#f2c99f'),
 dict(id='apple',name='りんごの詰め合わせ',category='果物',region='長野',season='冬',price=2400,amount='3kg',stock=5,producer='orchard',emoji='🍎',color='#efc0b2'),
 dict(id='rice',name='白米',category='米',region='千葉',season='秋',price=3500,amount='5kg',stock=4,producer='field',emoji='🌾',color='#e9dfb4'),
 dict(id='jam',name='果実ジャム',category='その他',region='長野',season='通年',price=780,amount='150g',stock=0,producer='orchard',emoji='🫙',color='#d9c6de'),
]
PRODUCERS=[dict(id='field',name='畑の便り（架空）',text='野菜やお米を紹介する、生産者ページの表示サンプルです。実在する農園ではありません。'),dict(id='orchard',name='果樹園の便り（架空）',text='果物や加工品を紹介する、生産者ページの表示サンプルです。実在する農園ではありません。')]
POLICIES={
 'legal':('特定商取引法に基づく表記','現在は販売を行わないデモです。販売主体・住所・電話番号・責任者・支払方法・支払時期・引渡時期は未確定です。これらの確認と適切な表示を完了するまで、実際の注文受付・課金は開始しません。'),
 'privacy':('プライバシーポリシー','デモ購入に氏名・住所・連絡先は入力しません。カートとデモ注文記録はこのブラウザー内に保存され、運営者へ送信されません。「端末のデモデータを削除」で削除できます。修理ガイドのアクセス解析は既存の方針をご確認ください。'),
 'terms':('利用規約','本サイトの商品・生産者・価格・在庫はすべて操作確認用の架空データです。デモの完了によって売買契約は成立せず、発送も課金もありません。端末内データは削除・変更される場合があり、注文管理の正式な記録には使用できません。'),
 'shipping':('配送・返品・返金ポリシー','デモ送料は配送先の都道府県と生産者ごとに計算します。通常地域800円、北海道・沖縄1,500円です。離島・冷蔵便等の実条件は未確定です。デモは発送・支払いがないため返品・返金も発生しません。実販売前に配送責任、返品条件、不良品対応、キャンセル期限を確定して公開します。'),
 'contact':('お問い合わせ','現在、お問い合わせの受付先は未設定です。この画面から連絡は送れません。実販売を始める前に、運営者の連絡先と問い合わせ方法を公開します。個人情報や購入依頼を入力しないでください。'),
}

def build(root):
 paths=['','products/','producers/','cart/','checkout/','complete/','orders/']+[f'products/{p["id"]}/' for p in PRODUCTS]+[f'producers/{p["id"]}/' for p in PRODUCERS]+[f'{k}/' for k in POLICIES]
 for p in PRODUCTS:
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="480" viewBox="0 0 640 480"><rect width="640" height="480" fill="{p["color"]}"/><text x="320" y="260" text-anchor="middle" font-size="130">{p["emoji"]}</text><text x="320" y="420" text-anchor="middle" font-size="24" fill="#263e31">DEMO / イメージイラスト</text></svg>'
  os.makedirs(os.path.join(root,'shop','images'),exist_ok=True)
  open(os.path.join(root,'shop','images',p['id']+'.svg'),'w').write(svg)
 open(os.path.join(root,'shop','catalog.json'),'w').write(json.dumps(dict(products=PRODUCTS,producers=PRODUCERS),ensure_ascii=False))
 for path in paths:
  entry=next((p['name'] for p in PRODUCTS if path==f"products/{p['id']}/"),None) or next((p['name'] for p in PRODUCERS if path==f"producers/{p['id']}/"),None)
  title=entry or POLICIES.get(path.rstrip('/'),('',))[0] or ('産地のマーケット' if not path else '商品と生産者を探す')
  policy=POLICIES.get(path.rstrip('/'))
  content=f'<h1>{policy[0]}</h1><p>{policy[1]}</p><h2>公開状況</h2><p>実販売は開始していません。</p>' if policy else '<h1>産地のマーケット</h1><h2>農産物を探す</h2><p>商品を読み込んでいます。JavaScriptを有効にしてください。</p><h2>作り手を知る</h2><a href="/producers/">生産者一覧へ</a>'
  text=f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}｜農産物の産直マーケット体験サイト</title><meta name="description" content="野菜・果物・米を探せる産直マーケットの操作体験です。商品と生産者は架空のデモデータ。実際の注文、決済、発送は行いません。機械修理ガイドも引き続き利用できます。"><link rel="canonical" href="https://agri.shiokonbu.com/{path}"><meta name="robots" content="{'index,follow' if not path or policy else 'noindex,follow'}"><link rel="stylesheet" href="/shop/store.css"><script src="/shop/store.js" defer></script></head><body><a class="skip" href="#content">本文へ</a><div class="notice">操作体験用デモ — 商品・生産者は架空です。注文・課金・発送はありません。</div><header><a class="brand" href="/">産地のマーケット<span>畑から届く暮らしを、ここから。</span></a><nav aria-label="メイン"><a href="/products/">商品を探す</a><a href="/producers/">生産者</a><a href="/cart/">カート <b id="count">0</b></a></nav></header><main id="content" tabindex="-1">{content}</main><footer><h2>産地のマーケットについて</h2><p>生産者と食卓をつなぐサービスのデモです。実商品の掲載許諾と販売体制を確認してから販売を開始します。</p><nav>{''.join(f'<a href="/{k}/">{v[0]}</a>' for k,v in POLICIES.items())}<a href="/orders/">端末のデモ注文記録</a><a href="/repair/">機械修理さがし</a></nav><button id="clear" type="button">端末のデモデータを削除</button><p id="storage-status" role="status"></p></footer></body></html>'''
  os.makedirs(os.path.join(root,path),exist_ok=True)
  open(os.path.join(root,path,'index.html'),'w').write(text)
 return [p for p in paths if not p or p.rstrip('/') in POLICIES]
