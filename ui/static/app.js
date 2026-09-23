const consoleEl = document.getElementById('console');
const buttons = [...document.querySelectorAll('button[data-action]')];

async function api(path, method='GET') {
  const r = await fetch(path, {method});
  return await r.json();
}

function setBusy(busy) { buttons.forEach(b => b.disabled = busy); }

function renderResults(payload) {
  const model = payload?.model;
  const bench = payload?.benchmark;
  const hasAny = model || bench;
  document.getElementById('empty-state').classList.toggle('hidden', !!hasAny);
  document.getElementById('result-grid').classList.toggle('hidden', !hasAny);
  document.getElementById('bars').classList.toggle('hidden', !bench);

  if (model) document.getElementById('accuracy').textContent = (model.float_accuracy_train * 100).toFixed(1) + '%';
  if (bench) {
    document.getElementById('cpu-cycles').textContent = bench.baseline_cycles_est;
    document.getElementById('accel-cycles').textContent = bench.accelerator_cycles_est;
    document.getElementById('speedup').textContent = Number(bench.speedup_est).toFixed(2) + '×';
    const max = Math.max(bench.baseline_cycles_est, bench.accelerator_cycles_est);
    document.getElementById('cpu-bar').style.width = (100 * bench.baseline_cycles_est/max) + '%';
    document.getElementById('accel-bar').style.width = (100 * bench.accelerator_cycles_est/max) + '%';
  }
}

buttons.forEach(button => button.addEventListener('click', async () => {
  const action = button.dataset.action;
  consoleEl.textContent = 'Running ' + action + '...';
  setBusy(true);
  try {
    const data = await api('/api/' + action, 'POST');
    consoleEl.textContent = data.output || (data.ok ? 'Done.' : 'Failed.');
    const results = await api('/api/results');
    renderResults(results);
  } catch (e) {
    consoleEl.textContent = 'Error: ' + e;
  } finally { setBusy(false); }
}));

api('/api/results').then(renderResults).catch(() => {});
