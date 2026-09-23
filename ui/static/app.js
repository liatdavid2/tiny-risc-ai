const $ = id => document.getElementById(id);
const names = {
  logistic_regression:'Logistic Regression',
  decision_tree:'Decision Tree',
  random_forest:'Random Forest',
  mlp_classifier:'MLP Classifier'
};
const order = Object.keys(names);
function setStatus(t){ $('status').textContent=t; }
function state(id,text,kind=''){ const e=$(id); e.textContent=text; e.className='state '+kind; }
async function post(url,body={}){
  const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const d=await r.json(); if(!r.ok) throw new Error(d.output||'Request failed'); return d;
}
function renderTraining(data){
  const box=$('trainingResults'); box.classList.remove('muted');
  box.innerHTML=order.map(k=>{ const m=data.models[k]; return `<div class="model-card"><b>${names[k]}</b><span>Training accuracy</span><strong>${(m.accuracy*100).toFixed(1)}%</strong><small>Train time ${m.train_ms.toFixed(1)} ms</small></div>`; }).join('');
}
function pct(v){ return (v*100).toFixed(1)+'%'; }
function renderBatch(data){
  const s=$('batchSummary').children;
  s[0].querySelector('strong').textContent=data.samples;
  s[1].querySelector('strong').textContent=data.class_counts['0'] ?? 0;
  s[2].querySelector('strong').textContent=data.class_counts['1'] ?? 0;
  const by=Object.fromEntries(data.models.map(x=>[x.model,x]));
  document.querySelectorAll('.batch-row').forEach(row=>{
    const m=by[row.dataset.model], cells=row.querySelectorAll('div');
    cells[0].innerHTML=`<strong>${pct(m.agreement)}</strong><small>agreement<br>CPU acc ${pct(m.cpu_accuracy)} · host acc ${pct(m.host_accuracy)}<br>${m.mismatches} mismatches</small>`;
    cells[1].innerHTML=`<strong>${m.host_inference_ms.toFixed(3)} ms</strong><small>${m.host_avg_us_per_sample.toFixed(2)} µs / sample</small>`;
    cells[2].innerHTML=`<strong>${m.cpu_avg_cycles_per_sample.toFixed(1)} cycles</strong><small>${m.cpu_total_cycles} total<br>${m.cpu_min_cycles}–${m.cpu_max_cycles} / sample</small>`;
    row.classList.toggle('match',m.agreement===1); row.classList.toggle('mismatch',m.agreement<1);
  });
}
$('trainBtn').onclick=async()=>{
  $('trainBtn').disabled=true; $('batchBtn').disabled=true;
  try{ state('trainState','running…','running'); setStatus('Training Logistic Regression, Decision Tree, Random Forest and MLP on the computer…'); const d=await post('/api/train'); if(!d.ok) throw new Error(d.output||'Training failed'); renderTraining(d.data); state('trainState','done ✓','done'); state('inferState','ready',''); setStatus('Training complete. Choose maximum samples per class and run batch inference.'); }
  catch(e){ state('trainState','error','warn'); setStatus('ERROR: '+e.message); }
  finally{ $('trainBtn').disabled=false; $('batchBtn').disabled=false; }
};
$('batchBtn').onclick=async()=>{
  $('batchBtn').disabled=true;
  try{ const n=Math.max(1,Math.min(100,parseInt($('maxPerClass').value||'25',10))); $('maxPerClass').value=n; state('inferState','running…','running'); setStatus(`Running up to ${n} examples per class through sklearn and the TinyRISC SystemVerilog CPU…`); const d=await post('/api/batch-infer',{max_per_class:n}); if(!d.ok) throw new Error(d.output||'Batch inference failed'); renderBatch(d.data); state('inferState','done ✓','done'); setStatus(`Batch complete: ${d.data.samples} samples. Compare agreement, accuracy, host time and TinyRISC cycles.`); }
  catch(e){ state('inferState','error','warn'); setStatus('ERROR: '+e.message); }
  finally{ $('batchBtn').disabled=false; }
};
$('testsBtn').onclick=async()=>{ setStatus('Running SystemVerilog unit tests…'); try{const d=await post('/api/sv-tests'); setStatus(d.ok?'CPU block tests passed ✓':'CPU block tests failed');}catch(e){setStatus('ERROR: '+e.message);} };
