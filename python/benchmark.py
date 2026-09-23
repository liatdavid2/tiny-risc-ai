from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
model_path = ROOT / "results" / "model.json"
if not model_path.exists():
    raise SystemExit("results/model.json not found. Run: python python\\train_model.py")

m = json.loads(model_path.read_text())
x = m["input_sample_int8"]
w = m["weights_int8"]
b = m["bias_int32"]
score = sum(a*b_ for a,b_ in zip(x,w)) + b
pred = int(score >= 0)

# Educational cycle model: baseline = 4 MUL + 4 ADD + compare.
# Accelerator = packed load overhead + 1 DOT + compare.
baseline_cycles = 9
accelerator_cycles = 3
speedup = baseline_cycles / accelerator_cycles
result = {
    "input_int8": x,
    "weights_int8": w,
    "bias_int32": b,
    "score": score,
    "prediction": pred,
    "baseline_cycles_est": baseline_cycles,
    "accelerator_cycles_est": accelerator_cycles,
    "speedup_est": speedup,
    "note": "Cycle counts are an educational architectural estimate, not wall-clock timing."
}
(ROOT / "results" / "benchmark.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
