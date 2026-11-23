"""Attributed references, not enrolled sellers. No product offers."""
PROFILE_PHOTO_IDS = frozenset({"22251", "22446", "29326"})

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
 scenes=json.loads(Path(__file__).with_name('official_scene_photos.json').read_text(encoding='utf-8'))
 ids=Counter(r['id'] for r in rows)
 if any(count != 1 for count in ids.values()):
  raise ValueError('Duplicate producer ID')
 valid_evidence={'profile_record','legacy_profile_record','listing_record'}
 for r in rows:
  if not re.fullmatch(r'[0-9]+',r['id']) or not r['name'] or not r['region'] or r['evidence_kind'] not in valid_evidence:
   raise ValueError('Invalid producer reference')
  goods=r['commodities']
  locality=r.get('locality')
  # These are discovery facts, never offers. Check history stays in the source seed.
  short_place=locality or r['region']
  useful_goods=goods if goods and goods not in {'農産物','農作物'} else None
  summary=r.get('profile_note') or (f'{short_place}。取扱品目の例：{useful_goods}。' if useful_goods else None)
  evidence=[]
  if locality:
   evidence.append(dict(field='locality',text=locality if r['region'] in locality else r['region']+locality))
  if useful_goods:
   evidence.append(dict(field='commodities',text=useful_goods))
  photo = {}
  if r['id'] in PROFILE_PHOTO_IDS:
   relative = f"shop/images/producers/{r['id']}.jpg"
   if not (Path(__file__).resolve().parent.parent / relative).is_file():
    raise ValueError(f'Missing verified photo: {relative}')
   photo = dict(photo='/' + relative)
  elif r['id'] in scenes:
   photo = scenes[r['id']]
   relative = f"shop/images/producers/{r['id']}.jpg"
   if photo['photo'] != '/' + relative or not (Path(__file__).resolve().parent.parent / relative).is_file():
    raise ValueError(f'Missing or mismatched verified scene photo: {relative}')
  # Profile/listing metadata is not an offer or an audience/category eligibility rule.
  yield dict(
   id='tabechoku-'+r['id'],name=r['name'],region=r['region'],categories=[],audiences=[],frequency=[],
   smallLot=None,minimum=None,commodities=useful_goods,locality=locality,summary=summary,evidence=evidence,
   url='https://www.tabechoku.com/producers/'+r['id'],profileSource=r.get('profile_source'),
   kind='marketplace_reference',
   enrolled=False,availability='unknown',sourcePlatform='食べチョク',**photo,
  )
