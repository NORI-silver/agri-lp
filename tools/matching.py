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
 with open(os.path.join(root,'shop/references.json'),'w') as f:json.dump(REFERENCES,f,ensure_ascii=False,indent=2)
