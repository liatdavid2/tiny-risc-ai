const $ = id => document.getElementById(id);
const names = {
  logistic_regression:'Logistic Regression',
  decision_tree:'Decision Tree',
  random_forest:'Random Forest',
  mlp_classifier:'MLP Classifier'
};
const order = Object.keys(names);
const datasetDescriptions = {
  breast_cancer:'Breast Cancer Wisconsin · real binary dataset · TinyRISC v1 uses 4 real features (mean radius, texture, perimeter, area).',
  iris:'Iris · real 3-class dataset · all 4 original features are used.'
};
function setStatus(t){ $('status').textContent=t; }
function state(id,text,kind=''){ const e=$(id); e.textContent=text; e.className='state '+kind; }
async function post(url,body={}){
  const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const d=await r.json(); if(!r.ok) throw new Error(d.output||'Request failed'); return d;
}
function renderTraining(data){
  const box=$('trainingResults'); box.classList.remove('muted');
  $('datasetInfo').textContent = `${data.dataset_label} · ${data.n_classes} classes · features: ${data.features_used.join(', ')}`;
  $('datasetShape').textContent = `${data.rows} rows · ${data.features_used.length} features`;
  box.innerHTML=order.map(k=>{ const m=data.models[k]; return `<div class="model-card"><b>${names[k]}</b><span>Test accuracy</span><strong>${(m.accuracy*100).toFixed(1)}%</strong><small>Train time ${m.train_ms.toFixed(1)} ms</small></div>`; }).join('');
}
function pct(v){ return (v*100).toFixed(1)+'%'; }
function renderBatch(data){
  const summary=$('batchSummary');
  const classCards=Object.entries(data.class_counts).map(([c,n])=>{
    const label=(data.class_names && data.class_names[Number(c)]) || `Class ${c}`;
    return `<div><span>${label}</span><strong>${n}</strong></div>`;
  }).join('');
  summary.innerHTML=`<div><span>Samples</span><strong>${data.samples}</strong></div>${classCards}`;
  const by=Object.fromEntries(data.models.map(x=>[x.model,x]));
  document.querySelectorAll('.batch-row').forEach(row=>{
    const m=by[row.dataset.model], cells=row.querySelectorAll('div');
    cells[0].innerHTML=`<strong>${pct(m.agreement)}</strong><small>agreement<br>TinyRISC acc ${pct(m.cpu_accuracy)} · sklearn acc ${pct(m.host_accuracy)}<br>${m.mismatches} mismatches</small>`;
    cells[1].innerHTML=`<strong>${m.host_inference_ms.toFixed(3)} ms</strong><small>${m.host_avg_us_per_sample.toFixed(2)} µs / sample</small>`;
    cells[2].innerHTML=`<strong>${m.cpu_avg_cycles_per_sample.toFixed(1)} cycles</strong><small>${m.cpu_total_cycles} total<br>${m.cpu_min_cycles}–${m.cpu_max_cycles} / sample</small>`;
    row.classList.toggle('match',m.agreement===1); row.classList.toggle('mismatch',m.agreement<1);
  });
}
$('datasetSelect').onchange=()=>{
  $('datasetInfo').textContent=datasetDescriptions[$('datasetSelect').value];
  state('trainState','waiting',''); state('inferState','waiting','');
  setStatus('Dataset changed. Train all models before running batch inference.');
};
$('trainBtn').onclick=async()=>{
  $('trainBtn').disabled=true; $('batchBtn').disabled=true;
  const dataset=$('datasetSelect').value;
  try{ state('trainState','running…','running'); setStatus(`Training all four models on ${dataset}…`); const d=await post('/api/train',{dataset}); if(!d.ok) throw new Error(d.output||'Training failed'); renderTraining(d.data); state('trainState','done ✓','done'); state('inferState','ready',''); setStatus('Training complete. Choose maximum samples per class and run batch inference.'); }
  catch(e){ state('trainState','error','warn'); setStatus('ERROR: '+e.message); }
  finally{ $('trainBtn').disabled=false; $('batchBtn').disabled=false; }
};
$('batchBtn').onclick=async()=>{
  $('batchBtn').disabled=true;
  try{ const n=Math.max(1,Math.min(100,parseInt($('maxPerClass').value||'25',10))); $('maxPerClass').value=n; state('inferState','running…','running'); setStatus(`Running up to ${n} held-out test examples per class through sklearn and TinyRISC…`); const d=await post('/api/batch-infer',{max_per_class:n}); if(!d.ok) throw new Error(d.output||'Batch inference failed'); renderBatch(d.data); state('inferState','done ✓','done'); setStatus(`Batch complete: ${d.data.samples} samples. Compare agreement, accuracy, host time and TinyRISC cycles.`); }
  catch(e){ state('inferState','error','warn'); setStatus('ERROR: '+e.message); }
  finally{ $('batchBtn').disabled=false; }
};
$('testsBtn').onclick=async()=>{ setStatus('Running SystemVerilog unit tests…'); try{const d=await post('/api/sv-tests'); setStatus(d.ok?'CPU block tests passed ✓':'CPU block tests failed');}catch(e){setStatus('ERROR: '+e.message);} };

// ---- Architecture LEGO explorer ----
// Base TinyRISC is a fixed reference architecture. Optional architectures are
// complete alternative designs: the same core plus one mutually-exclusive MAC width.
let architectures = [
  {name:'Base TinyRISC', mac_lanes:0}
];
const ARCH_PRESETS = {
  2:{name:'TinyRISC + 2× MAC', mac_lanes:2},
  4:{name:'TinyRISC + 4× MAC', mac_lanes:4},
  8:{name:'TinyRISC + 8× MAC', mac_lanes:8}
};
function renderArchChips(){
  const box=$('archChips');
  box.innerHTML=architectures.map((a,i)=>{
    const fixed=a.mac_lanes===0;
    return `<div class="arch-chip ${fixed?'fixed-chip':''}"><b>${a.name}</b>${fixed?'<small>reference</small>':`<button data-i="${i}" title="Remove this architecture">×</button>`}</div>`;
  }).join('');
  box.querySelectorAll('button').forEach(b=>b.onclick=()=>{
    const i=Number(b.dataset.i);
    if(architectures[i] && architectures[i].mac_lanes!==0){
      architectures.splice(i,1);
      renderArchChips();
      setStatus('Architecture removed. Compare again to refresh the results.');
    }
  });
}
renderArchChips();
$('addArchBtn').onclick=()=>{
  const select=$('architecturePreset');
  const lanes=Number(select.value||0);
  if(!ARCH_PRESETS[lanes]){
    setStatus('Choose an architecture from the ADD ARCHITECTURE dropdown first.');
    return;
  }
  if(architectures.some(a=>a.mac_lanes===lanes)){
    setStatus(`${ARCH_PRESETS[lanes].name} is already in the comparison.`);
    return;
  }
  architectures.push({...ARCH_PRESETS[lanes]});
  architectures.sort((a,b)=>a.mac_lanes-b.mac_lanes);
  renderArchChips();
  select.value='';
  setStatus(`${ARCH_PRESETS[lanes].name} added. You can add another design or compare architectures.`);
};
function renderArchitectureCompare(data){
  const box=$('archResults'); box.classList.remove('muted');
  const archs=data.architectures;
  let html=`<div class="arch-cell head model-head">MODEL</div>`+archs.map(a=>`<div class="arch-cell head">${a.name}</div>`).join('');
  data.models.forEach(m=>{
    const vals=m.architectures.map(x=>x.avg_cycles), best=Math.min(...vals);
    html+=`<div class="arch-cell model">${names[m.model]}<small>${m.mac_ops_per_sample} MAC terms/sample</small></div>`;
    m.architectures.forEach(v=>{
      const cls=Math.abs(v.avg_cycles-best)<1e-9?'arch-cell best':'arch-cell';
      html+=`<div class="${cls}"><b>${v.avg_cycles.toFixed(1)}</b> cycles<small>${v.speedup_vs_base.toFixed(2)}× vs base</small></div>`;
    });
  });
  box.style.gridTemplateColumns=`170px repeat(${Math.max(1,archs.length)}, minmax(130px, 1fr))`;
  box.innerHTML=html;
}
$('archCompareBtn').onclick=async()=>{
  $('archCompareBtn').disabled=true;
  try{
    setStatus('Comparing your selected LEGO architectures using the completed TinyRISC batch workload…');
    const d=await post('/api/architecture-compare',{architectures});
    if(!d.ok) throw new Error(d.output||'Architecture comparison failed');
    renderArchitectureCompare(d.data);
    setStatus('Architecture comparison complete. Green cells use the fewest projected cycles for that model.');
  }catch(e){setStatus('ERROR: '+e.message);} finally{$('archCompareBtn').disabled=false;}
};

// ---- One-screen accordion navigation ----
function openPanel(panelId){
  document.querySelectorAll('.accordion-panel').forEach(p=>p.classList.toggle('active', p.id===panelId));
}
document.querySelectorAll('.accordion-head').forEach(h=>h.addEventListener('click',()=>openPanel(h.dataset.panel)));

// Wrap existing render functions so collapsed headers keep a useful summary.
const _renderTraining = renderTraining;
renderTraining = function(data){
  _renderTraining(data);
  const best = Math.max(...order.map(k=>data.models[k].accuracy));
  $('trainingSummary').textContent = `${data.dataset_label} · 4 models trained · best test accuracy ${(best*100).toFixed(1)}%`;
};
const _renderBatch = renderBatch;
renderBatch = function(data){
  _renderBatch(data);
  const agreements = data.models.map(m=>m.agreement*100);
  $('inferenceSummary').textContent = `${data.samples} samples · agreement ${Math.min(...agreements).toFixed(1)}–${Math.max(...agreements).toFixed(1)}% · sklearn vs TinyRISC`;
};
const _renderArchitectureCompare = renderArchitectureCompare;
renderArchitectureCompare = function(data){
  _renderArchitectureCompare(data);
  $('architectureSummary').textContent = `${data.architectures.length} architectures compared · Base TinyRISC kept as reference`;
  state('archState','done ✓','done');
};

// Move focus automatically through the three-stage story.
const _trainClick = $('trainBtn').onclick;
$('trainBtn').onclick = async function(){
  openPanel('trainingPanel');
  await _trainClick.call(this);
  if($('trainState').classList.contains('done')) openPanel('inferencePanel');
};
const _batchClick = $('batchBtn').onclick;
$('batchBtn').onclick = async function(){
  openPanel('inferencePanel');
  await _batchClick.call(this);
  if($('inferState').classList.contains('done')) openPanel('architecturePanel');
};
const _archClick = $('archCompareBtn').onclick;
$('archCompareBtn').onclick = async function(){
  openPanel('architecturePanel');
  state('archState','running…','running');
  await _archClick.call(this);
  if(!$('status').textContent.startsWith('ERROR')) state('archState','done ✓','done');
};
