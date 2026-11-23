"""Attributed references, not enrolled sellers. No third-party photos or product offers."""
REFERENCES = [
 dict(id='nishikaze',name='西風農園',region='福岡県',categories=['野菜'],audiences=['飲食店・事業者'],frequency=[],smallLot=True,minimum=None,
      summary='飲食店向けの野菜卸について、小ロットや品目・納品頻度の相談を案内しています。',
      evidence=[dict(field='smallLot',text='小ロットの相談を案内。具体的な最低数量は未確認。'),dict(field='audience',text='市内の飲食店・企業を中心とした卸販売の案内。全国への配送を意味しません。')],
      url='https://www.nishikaze-nouen.jp/wholesale/'),
 dict(id='oki',name='おき農園',region='福岡県',categories=['野菜'],audiences=['飲食店・事業者'],frequency=[],smallLot=None,minimum=None,
      summary='飲食店向けの取引相談窓口があります。天候などで希望する野菜が揃わない場合もあると案内しています。',
      evidence=[dict(field='schedule',text='発送は月〜金、締切は発送前日15時と案内。到着日や個別の受注可否は要確認。'),dict(field='availability',text='収穫状況によって希望品目が揃わない場合があるとの注意書き。')],
      url='https://okifarm-itoshima.com/#contact'),
 dict(id='kinameru',name='木菜米ルファーム',region='群馬県',categories=['野菜','米'],audiences=['飲食店・事業者'],frequency=['単発','定期'],smallLot=None,minimum=None,
      summary='米・野菜の仕入れについて、数量・時期・納品頻度・精米方法などの相談を案内しています。',
      evidence=[dict(field='frequency',text='野菜の単発・継続納品を相談できると案内。収穫状況の確認が必要。'),dict(field='spec',text='数量・希望時期・納品頻度・精米方法・規格・予算を伝えるよう案内。')],
      url='https://kinameru-farm.com/business-contact/'),
 dict(id='chiba',name='鎌倉山千葉農園',region='神奈川県',categories=['野菜'],audiences=['家庭用'],frequency=['定期'],smallLot=None,minimum=None,
      summary='家庭向けの旬野菜の定期便を案内しています。配送地域ごとの条件は公式サイトで確認できます。',
      evidence=[dict(field='audience',text='家庭向けの野菜定期便の案内。'),dict(field='frequency',text='隔週・月2回の野菜定期便を案内。送料は地域で変動。')],
      url='https://www.chiba-farm.world/subscription'),
]
for r in REFERENCES:
 r.update(checked='2026-11-23',kind='official_reference',enrolled=False,permission='not_obtained',availability='unknown')

def build(root):
 import json,os
 os.makedirs(os.path.join(root,'shop'),exist_ok=True)
 with open(os.path.join(root,'shop/references.json'),'w') as f:json.dump(REFERENCES + list(tabechoku_references()),f,ensure_ascii=False,indent=2)

def tabechoku_references():
 import json,re
 from pathlib import Path
 from collections import Counter
 rows=json.loads(Path(__file__).with_name('agri_producers.json').read_text(encoding='utf-8'))
 ids=Counter(r['id'] for r in rows)
 if any(count != 1 for count in ids.values()):
  raise ValueError('Duplicate producer ID')
 labels={
  'profile_record':'食べチョクの個別プロフィールを確認した記録があります。今回の直接再確認は未実施です。',
  'legacy_profile_record':'過去の取込記録に食べチョクの個別プロフィール確認があります。現在の内容は未確認です。',
  'listing_record':'食べチョクの一覧掲載の記録があります。個別プロフィールの内容は未確認です。',
 }
 for r in rows:
  if not re.fullmatch(r'[0-9]+',r['id']) or not r['name'] or not r['region'] or r['evidence_kind'] not in labels:
   raise ValueError('Invalid producer reference')
  goods=r['commodities']
  evidence=[dict(field='listing',text=labels[r['evidence_kind']])]
  if goods:
   evidence.append(dict(field='commodities',text='記録にある品目：'+goods+'。現在の販売品・在庫・配送は未確認。'))
  # Profile/listing metadata is not an offer or an audience/category eligibility rule.
  yield dict(
   id='tabechoku-'+r['id'],name=r['name'],region=r['region'],categories=[],audiences=[],frequency=[],
   smallLot=None,minimum=None,commodities=goods,summary=labels[r['evidence_kind']],evidence=evidence,
   url='https://www.tabechoku.com/producers/'+r['id'],checked='2026-11-23',
   kind='marketplace_reference',evidenceKind=r['evidence_kind'],sourceChecked=r.get('source_checked'),
   enrolled=False,availability='unknown',sourcePlatform='食べチョク',
  )
