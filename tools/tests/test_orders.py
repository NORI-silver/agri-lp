import unittest, tempfile, sys, os, sqlite3
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,os.path.abspath('server'))
import app
class Orders(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();app.DB=self.temp.name+'/orders.sqlite';app.init()
 def tearDown(self):self.temp.cleanup()
 def body(self,token='a'*20,q=1):return dict(id=token,items=[dict(id='carrot',quantity=q)],region='北海道')
 def test_totals_and_idempotency(self):
  a=app.order(self.body(q=2));self.assertEqual(a['total'],3460);self.assertEqual(a,app.order(self.body(q=2)))
  with sqlite3.connect(app.DB) as c:self.assertEqual(c.execute('SELECT quantity FROM stock WHERE id="carrot"').fetchone()[0],6)
 def test_content_change_rejected(self):
  app.order(self.body())
  with self.assertRaises(ValueError):app.order(self.body(q=2))
 def test_validation(self):
  for q in [0,-1,1.5,True,99]:
   with self.assertRaises(ValueError):app.order(self.body(q=q))
  body=self.body();body['region']='不明'
  with self.assertRaises(ValueError):app.order(body)
 def test_concurrent_stock(self):
  def run(i):
   try:app.order(self.body(str(i)*20,5));return True
   except ValueError:return False
  with ThreadPoolExecutor() as pool:self.assertEqual(sum(pool.map(run,range(2))),1)
 def test_rollback(self):
  b=self.body();b['items'].append(dict(id='jam',quantity=1))
  with self.assertRaises(ValueError):app.order(b)
  with sqlite3.connect(app.DB) as c:self.assertEqual(c.execute('SELECT quantity FROM stock WHERE id="carrot"').fetchone()[0],8)
if __name__=='__main__':unittest.main()
