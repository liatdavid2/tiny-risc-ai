const $ = id => document.getElementById(id);
const names = {
  logistic_regression:'Logistic Regression',
  decision_tree:'Decision Tree',
  random_forest:'Random Forest',
  mlp_classifier:'MLP Classifier'
};
const order = Object.keys(names);

function setStatus(text){ $('status').textContent=text; }
function state(id,text,kind=''){ const e=$(id); e.textContent=text; e.className='state '+kind; }
async function post(url){
  const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'}});
  return await r.json();
}
function renderTraining(data){
  const box=$('trainingResults');
  box.classList.remove('muted');
  box.innerHTML=order.map(k=>{
    const m=data.models[k];
    return `<div class="model-card"><b>${names[k]}</b><span>Training accuracy</span><strong>${(m.accuracy*100).toFixed(1)}%</strong><small>sklearn prediction sample: ${m.sklearn_prediction}</small></div>`;
  }).join('');
}
function renderComparison(models,cpu){
  const byModel=Object.fromEntries(cpu.map(x=>[x.model,x]));
  document.querySelectorAll('.compare-row').forEach(row=>{
    const k=row.dataset.model, host=models.models[k].sklearn_prediction, c=byModel[k];
    const vals=row.querySelectorAll('strong');
    vals[0].textContent=host;
    vals[1].textContent=c?.prediction ?? 'ERR';
    row.querySelector('em').innerHTML=c ? `${c.cycles} cycles<br><small>${c.program_instructions} instr in IMEM</small>` : '—';
    row.classList.toggle('match',c && c.prediction===host);
    row.classList.toggle('mismatch',!c || c.prediction!==host);
    row.querySelector('i').textContent=(c && c.prediction===host)?'✓':'≠';
  });
}

$('runAllBtn').onclick=async()=>{
  $('runAllBtn').disabled=true;
  try{
    state('trainState','running…','running');
    state('inferState','waiting');
    setStatus('Phase 1/2: training all sklearn models on the computer…');
    const tr=await post('/api/train');
    if(!tr.ok) throw new Error(tr.output||'Training failed');
    renderTraining(tr.data);
    state('trainState','done ✓','done');

    state('inferState','running…','running');
    setStatus('Phase 2/2: loading programs into Instruction Memory and executing inference + control flow inside TinyRISC…');
    const inf=await post('/api/cpu-infer-all');
    if(!inf.data) throw new Error(inf.output||'CPU inference failed');
    renderComparison(inf.models,inf.data);
    state('inferState',inf.ok?'done ✓':'completed with mismatch',inf.ok?'done':'warn');
    setStatus(inf.ok?'All models trained and predictions match the TinyRISC CPU ✓':'Finished. Check highlighted prediction differences.');
  }catch(e){
    setStatus('ERROR: '+e.message);
    state('inferState','error','warn');
  }finally{$('runAllBtn').disabled=false;}
};

$('testsBtn').onclick=async()=>{
  setStatus('Running SystemVerilog unit tests for the CPU blocks…');
  const d=await post('/api/sv-tests');
  setStatus(d.ok?'CPU block tests passed ✓':'CPU block tests failed — check container log');
};
