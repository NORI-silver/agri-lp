"""Explicit demo storefront. No real orders, payments or personal data collection."""
import json, os, html
import matching
import store_layout
PRODUCTS = [
 dict(id='carrot',name='土付きにんじん',category='野菜',region='千葉',season='冬',price=980,amount='1kg',stock=8,producer='field',emoji='🥕',color='#f2c99f'),
 dict(id='apple',name='りんごの詰め合わせ',category='果物',region='長野',season='冬',price=2400,amount='3kg',stock=5,producer='orchard',emoji='🍎',color='#efc0b2'),
 dict(id='rice',name='白米',category='米',region='千葉',season='秋',price=3500,amount='5kg',stock=4,producer='field',emoji='🌾',color='#e9dfb4'),
 dict(id='jam',name='果実ジャム',category='その他',region='長野',season='通年',price=780,amount='150g',stock=0,producer='orchard',emoji='🫙',color='#d9c6de'),
]
PRODUCERS=[dict(id='field',name='畑の便り（架空）',text='野菜やお米を紹介する、生産者ページの表示サンプルです。実在する農園ではありません。'),dict(id='orchard',name='果樹園の便り（架空）',text='果物や加工品を紹介する、生産者ページの表示サンプルです。実在する農園ではありません。')]
POLICIES={
 'legal':('特定商取引法に基づく表記','現在は公式公開情報の参照・比較と相談文作成に対応しています。サイト自身による販売・注文受付は行いません。販売主体・住所・電話番号・責任者・支払方法・支払時期・引渡時期は未確定です。これらの確認と適切な表示を完了するまで、実際の注文受付・課金は開始しません。'),
 'privacy':('プライバシーポリシー','希望条件・相談の下書き・比較先はこの端末内に保存します。生産者や運営者へ自動送信しません。公式サイトへ移動した後の情報の取り扱いは移動先の方針をご確認ください。氏名・住所・連絡先はこのサイトに入力しないでください。カートとデモ注文記録はこのブラウザー内に保存され、運営者へ送信されません。「端末に保存したデータを削除」で削除できます。修理ガイドのアクセス解析は既存の方針をご確認ください。'),
 'terms':('利用規約','公式情報の参照先は、登録・提携・掲載許諾を確認した生産者ではありません。公開情報は現在の受付や個別条件への適合を保証しません。購入機能にある商品・生産者・価格・在庫は操作確認用の架空データです。デモの完了によって売買契約は成立せず、発送も課金もありません。端末内データは削除・変更される場合があり、注文管理の正式な記録には使用できません。'),
 'shipping':('配送・返品・返金ポリシー','デモ送料は配送先の都道府県と生産者ごとに計算します。通常地域800円、北海道・沖縄1,500円です。離島・冷蔵便等の実条件は未確定です。デモは発送・支払いがないため返品・返金も発生しません。実販売前に配送責任、返品条件、不良品対応、キャンセル期限を確定して公開します。'),
 'contact':('お問い合わせ','サイト運営者への問い合わせ受付先は未設定です。農産物の取引相談は、生産者の公式サイトに記載された窓口で行ってください。このサイトから相談の自動送信は行いません。実販売を始める前に、運営者の連絡先と問い合わせ方法を公開します。個人情報や購入依頼を入力しないでください。'),
}

def build(root):
 matching.build(root)
 paths=['','match/','requests/','for-producers/','compare/','inquiry/','how-it-works/','products/','producers/','cart/','checkout/','complete/','orders/']+[f'products/{p["id"]}/' for p in PRODUCTS]+[f'producers/{p["id"]}/' for p in PRODUCERS]+[f'{k}/' for k in POLICIES]
 for p in PRODUCTS:
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="480" viewBox="0 0 640 480"><rect width="640" height="480" fill="{p["color"]}"/><text x="320" y="260" text-anchor="middle" font-size="130">{p["emoji"]}</text><text x="320" y="420" text-anchor="middle" font-size="24" fill="#263e31">DEMO / イメージイラスト</text></svg>'
  os.makedirs(os.path.join(root,'shop','images'),exist_ok=True)
  open(os.path.join(root,'shop','images',p['id']+'.svg'),'w').write(svg)
 open(os.path.join(root,'shop','catalog.json'),'w').write(json.dumps(dict(products=PRODUCTS,producers=PRODUCERS),ensure_ascii=False))
 for path in paths:
  entry=next((p['name'] for p in PRODUCTS if path==f"products/{p['id']}/"),None) or next((p['name'] for p in PRODUCERS if path==f"producers/{p['id']}/"),None)
  title=entry or POLICIES.get(path.rstrip('/'),('',))[0] or ('産地のつながり' if not path else {'match/':'条件を整理して生産者を探す','producers/':'生産者の公式窓口を探す','requests/':'保存した相談の下書き','for-producers/':'生産者の方へ','compare/':'選んだ相談先を比較する','inquiry/':'相談文を用意して公式窓口へ','how-it-works/':'産地のつながりのご利用ガイド'}.get(path,'商品と生産者を探す'))
  policy=POLICIES.get(path.rstrip('/'))
  content=f'<h1>{policy[0]}</h1><p>{policy[1]}</p><h2>公開状況</h2><p>実販売は開始していません。</p>' if policy else '<h1>欲しい農産物から、作り手とつながる。</h1><p>用途・品目・規格・数量・納品頻度などの希望を整理し、公式情報を比較して相談文を作れます。</p><h2>希望条件から相談先を探す</h2><p>条件検索と比較にはJavaScriptを有効にしてください。各生産者への相談は公式サイトの窓口で行えます。</p><h2>生産者の公式情報</h2><p>以下は公開情報への参照です。登録・提携を確認した生産者一覧ではなく、現在の受付可否は未確認です。</p><ul>' + ''.join(f'<li><a href="{html.escape(r["url"])}" rel="noopener noreferrer">{html.escape(r["name"])}</a>（公式情報）</li>' for r in matching.REFERENCES) + '</ul><a href="/producers/">参照先を比較する</a>'
  text=store_layout.render(root, path, title, content, POLICIES)
  os.makedirs(os.path.join(root,path),exist_ok=True)
  open(os.path.join(root,path,'index.html'),'w').write(text)
 return [p for p in paths if not p or p.rstrip('/') in POLICIES]
