const $=id=>document.getElementById(id);
const maps={
  logistic_regression:['weights + bias','Dot product + bias + sign compare'],
  decision_tree:['thresholds + nodes','Threshold compare + branch'],
  random_forest:['multiple trees','Tree inference + majority voting'],
  mlp_classifier:['layer weights','Matrix multiply + ReLU + output layer']
};
function status(s){$('toast').textContent=s}
function resetMetrics(){['acc','expected','pred','cpuCycles','hwCycles','speedup'].forEach(x=>$(x).textContent='—')}
function updateMap(){const v=$('model').value;$('exportBrick').textContent=maps[v][0];$('mapText').textContent=maps[v][1];resetMetrics()}
async function post(url,body){status('Running…');const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:body?JSON.stringify(body):null});const d=await r.json();status(d.ok?'Done ✓':(d.output||'Failed'));return d}
$('model').onchange=updateMap;
$('trainBtn').onclick=async()=>{const d=await post('/api/train');if(d.data){const m=d.data.models[$('model').value];$('acc').textContent=(m.accuracy*100).toFixed(1)+'%';$('expected').textContent=m.sklearn_prediction}}
$('inferBtn').onclick=async()=>{const name=$('model').value;const d=await post('/api/infer',{model:name});if(d.data){$('acc').textContent=(d.data.train_accuracy*100).toFixed(1)+'%';$('expected').textContent=d.data.expected;$('pred').textContent=d.data.prediction;$('cpuCycles').textContent=d.data.cycles.cpu_style;$('hwCycles').textContent=d.data.cycles.specialized_engine;$('speedup').textContent=d.data.speedup_est.toFixed(1)+'×';$('note').textContent='* '+d.data.cycles.explanation+' Prediction executed in SystemVerilog.'}}
$('testBtn').onclick=()=>post('/api/sv-tests');
updateMap();
