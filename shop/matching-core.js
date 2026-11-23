/* Public information is evidence of a published condition, never of current acceptance. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.AgriMatchCore=factory();})(globalThis,()=>{
 const fields={audience:'利用目的',category:'品目の分類',item:'希望品目・品種',frequency:'納品頻度',smallLot:'小口相談',budget:'予算',quantity:'数量',destination:'配送先',date:'希望日',spec:'規格・熟度など',availability:'現在の受付'};
 function evaluate(ref,request){
  const results=[],add=(field,state,note)=>results.push({field,label:fields[field],state,note});
  for(const [field,key]of [['audience','audiences'],['category','categories'],['frequency','frequency']])if(request[field])add(field,(ref[key]||[]).includes(request[field])?'published':'unknown',(ref[key]||[]).includes(request[field])?'公式案内に記載あり。個別条件は要確認。':'公式情報からは判断できません。');
  if(request.smallLot)add('smallLot',ref.smallLot===true?'published':ref.smallLot===false?'no':'unknown',ref.smallLot===true?'小口の相談案内あり。指定数量の受注保証ではありません。':'具体的な小口条件は要確認。');
  if(request.budget)add('budget',Number.isFinite(ref.minimum)?Number(request.budget)>=ref.minimum?'published':'no':'unknown',Number.isFinite(ref.minimum)?`公表最低注文額 ${ref.minimum.toLocaleString('ja-JP')}円。送料・個別見積りは別途確認。`:'この予算で購入できるかは未確認。');
  for(const field of ['item','quantity','destination','date','spec'])if(request[field])add(field,'unknown','個別の希望条件は、生産者へ確認が必要です。');
  add('availability','unknown','現在の在庫・受付可否・返信時期は未確認です。');
  return {ref,results,published:results.filter(r=>r.state==='published'),unknown:results.filter(r=>r.state==='unknown'),excluded:results.some(r=>r.state==='no')};
 }
 function brief(request,refs){
  const lines=['農産物のお取引について相談です。',''];
  for(const [field,label]of Object.entries(fields)){if(field==='availability')continue;const value=field==='smallLot'?(request.smallLot?'少量からの相談を希望':null):request[field];if(value)lines.push(`${label}：${value}${field==='budget'?'円／1回（税込・送料別の希望額）':''}`);}
  lines.push('','希望条件での対応可否、見積り（商品代・送料・その他費用）、納品可能日、支払条件、返品・欠品時の対応をご教示ください。','この文章は問い合わせ用です。発注・契約の確定ではありません。');
  if(refs.length)lines.push('','確認先：'+refs.map(r=>r.name).join('、'));
  return lines.join('\n');
 }
 return {evaluate,brief,fields};
});
