const assert=require('node:assert/strict');const core=require('../../shop/matching-core.js');const refs=require('../../shop/references.json');
const rice=refs.find(r=>r.id==='kinameru');let r=core.evaluate(rice,{category:'米',audience:'飲食店・事業者',quantity:'20kg',destination:'北海道',date:'2099-01-01',frequency:'定期'});
assert.equal(r.published.length,3);assert.equal(r.excluded,false);for(const k of ['quantity','destination','date','availability'])assert.equal(r.results.find(x=>x.field===k).state,'unknown');
r=core.evaluate(rice,{category:'果物',smallLot:true});assert.equal(r.results.find(x=>x.field==='category').state,'unknown');assert.equal(r.results.find(x=>x.field==='smallLot').state,'unknown');assert.equal(r.excluded,false);
r=core.evaluate({...rice,minimum:5000},{budget:3000});assert.equal(r.excluded,true);assert.equal(r.results.find(x=>x.field==='budget').state,'no');
r=core.evaluate({...rice,minimum:5000},{budget:5000});assert.equal(r.results.find(x=>x.field==='budget').state,'published');assert.equal(r.results.find(x=>x.field==='availability').state,'unknown');
const text=core.brief({category:'野菜',item:'にんじん',quantity:'5kg',budget:'3000',smallLot:true},[rice]);assert.match(text,/にんじん/);assert.match(text,/5kg/);assert.match(text,/3?000円/);assert.match(text,/発注・契約の確定ではありません/);
assert.ok(refs.every(r=>r.kind==='official_reference'&&!r.enrolled&&r.permission==='not_obtained'&&r.checked&&r.url.startsWith('https://')));
console.log('PASS: matching evidence states, unknown preservation, explicit budget conflict, no acceptance inference, brief fields, reference provenance.');
