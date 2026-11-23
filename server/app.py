#!/usr/bin/env python3
"""Local/test demo order API; never accepts payment or customer PII.
Run: AGRI_DB=/tmp/agri-demo.sqlite python3 server/app.py
Production checkout remains disabled. No external dependencies.
"""
import sys, os, sqlite3, json, re, secrets
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from store import PRODUCTS
DB=os.environ.get('AGRI_DB','/tmp/agri-demo.sqlite')
REGIONS='北海道 青森県 岩手県 宮城県 秋田県 山形県 福島県 茨城県 栃木県 群馬県 埼玉県 千葉県 東京都 神奈川県 新潟県 富山県 石川県 福井県 山梨県 長野県 岐阜県 静岡県 愛知県 三重県 滋賀県 京都府 大阪府 兵庫県 奈良県 和歌山県 鳥取県 島根県 岡山県 広島県 山口県 徳島県 香川県 愛媛県 高知県 福岡県 佐賀県 長崎県 熊本県 大分県 宮崎県 鹿児島県 沖縄県'.split()
def init():
 with sqlite3.connect(DB) as c:
  c.execute('CREATE TABLE IF NOT EXISTS stock (id TEXT PRIMARY KEY, quantity INTEGER NOT NULL CHECK(quantity>=0))')
  c.execute('CREATE TABLE IF NOT EXISTS orders (id TEXT PRIMARY KEY, request TEXT NOT NULL, data TEXT NOT NULL, created TEXT DEFAULT CURRENT_TIMESTAMP)')
  c.executemany('INSERT OR IGNORE INTO stock VALUES (?,?)',[(p['id'],p['stock']) for p in PRODUCTS])
def order(body):
 if not isinstance(body,dict) or set(body)!={'id','items','region'}:raise ValueError('入力項目が不正です')
 token,items,region=body['id'],body['items'],body['region']
 if not isinstance(token,str) or not re.fullmatch(r'[A-Za-z0-9-]{16,80}',token):raise ValueError('注文識別子が不正です')
 if region not in REGIONS or not isinstance(items,list) or not 1<=len(items)<=20:raise ValueError('配送先または商品が不正です')
 catalog={p['id']:p for p in PRODUCTS};seen=set();total=0;farmers=set()
 for item in items:
  if not isinstance(item,dict) or set(item)!={'id','quantity'}:raise ValueError('商品が不正です')
  pid,q=item['id'],item['quantity']
  if not isinstance(pid,str) or pid not in catalog or pid in seen or type(q)!=int or not 1<=q<=99:raise ValueError('数量または商品が不正です')
  seen.add(pid);p=catalog[pid];total+=p['price']*q;farmers.add(p['producer'])
 payload=json.dumps(body,sort_keys=True)
 with sqlite3.connect(DB,timeout=10) as c:
  c.execute('BEGIN IMMEDIATE')
  existing=c.execute('SELECT request,data FROM orders WHERE id=?',(token,)).fetchone()
  if existing:
   if existing[0]!=payload:raise ValueError('同じ識別子で内容を変更できません')
   return json.loads(existing[1])
  for item in items:
   if c.execute('UPDATE stock SET quantity=quantity-? WHERE id=? AND quantity>=?',(item['quantity'],item['id'],item['quantity'])).rowcount!=1:raise ValueError('在庫が不足しています')
  shipping=len(farmers)*(1500 if region in ['北海道','沖縄県'] else 800)
  result=dict(id=token,demo=True,items=[dict(**x,price=catalog[x['id']]['price']) for x in items],shipping=shipping,total=total+shipping)
  c.execute('INSERT INTO orders(id,request,data) VALUES (?,?,?)',(token,payload,json.dumps(result)))
  return result
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a):pass
 def reply(self,status,data):
  b=json.dumps(data,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  if self.path=='/api/admin/orders':
   token=os.environ.get('AGRI_ADMIN_TOKEN','')
   if not token or not secrets.compare_digest(self.headers.get('Authorization',''),'Bearer '+token):self.reply(403,{'error':'管理者認証が必要です'});return
   with sqlite3.connect(DB) as c:rows=c.execute('SELECT data,created FROM orders ORDER BY created DESC LIMIT 100').fetchall()
   self.reply(200,[dict(json.loads(r[0]),created=r[1]) for r in rows]);return
  if self.path=='/shop/runtime.json':
   self.reply(200,{'orderEndpoint':'/api/orders'});return
  if self.path=='/shop/catalog.json':
   data=json.loads((ROOT/'shop/catalog.json').read_text())
   with sqlite3.connect(DB) as c:stock=dict(c.execute('SELECT id,quantity FROM stock'))
   for p in data['products']:p['stock']=stock[p['id']]
   self.reply(200,data);return
  # Never serve repository internals, DB, tests or configuration through the web server.
  path=self.path.split('?')[0]
  if any(x.startswith('.') for x in path.split('/') if x) or path.startswith(('/server/','/tools/','/docs/')) or '..' in path or '%' in path:
   self.reply(404,{'error':'見つかりません'});return
  return super().do_GET()
 def do_HEAD(self):
  self.send_response(405);self.end_headers()
 def do_POST(self):
  if self.path!='/api/orders':self.reply(404,{'error':'見つかりません'});return
  origin=self.headers.get('Origin')
  if origin and origin!='http://'+self.headers.get('Host',''):self.reply(403,{'error':'送信元が不正です'});return
  try:
   size=int(self.headers.get('Content-Length','0'))
   if not 0<size<=8192:raise ValueError('入力が大きすぎます')
   data=json.loads(self.rfile.read(size));result=order(data)
  except (ValueError,TypeError,KeyError):self.reply(400,{'error':'入力内容または在庫を確認してください'});return
  except sqlite3.Error:self.reply(503,{'error':'保存できませんでした。時間をおいてお試しください'});return
  self.reply(200,result)
if __name__=='__main__':
 init();ThreadingHTTPServer(('127.0.0.1',int(os.environ.get('PORT','8874'))),Handler).serve_forever()
