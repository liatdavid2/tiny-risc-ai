from pathlib import Path
import argparse, json, subprocess, re, sys
ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "generated"
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
MODELS = {
    "logistic_regression": ("logistic_inference.sv", "logistic_tb.sv"),
    "decision_tree": ("decision_tree_inference.sv", "decision_tree_tb.sv"),
    "random_forest": ("random_forest_inference.sv", "random_forest_tb.sv"),
    "mlp_classifier": ("mlp_inference.sv", "mlp_tb.sv"),
}
parser = argparse.ArgumentParser()
parser.add_argument("--model", choices=list(MODELS) + ["all"], default="all")
args = parser.parse_args()
if not (OUT / "models_summary.json").exists():
    subprocess.run([sys.executable, str(ROOT / "python" / "train_models.py")], cwd=ROOT, check=True)

def one(name):
    rtl, tb = MODELS[name]
    exe = OUT / f"{name}.out"
    cp = subprocess.run(["iverilog", "-g2012", "-o", str(exe), str(GEN/rtl), str(GEN/tb)], cwd=ROOT, capture_output=True, text=True)
    if cp.returncode:
        return {"ok": False, "model": name, "output": cp.stdout + cp.stderr}
    rp = subprocess.run(["vvp", str(exe)], cwd=ROOT, capture_output=True, text=True)
    text = rp.stdout + rp.stderr
    m = re.search(r"RESULT prediction=(\d+) expected=(\d+)", text)
    pred = int(m.group(1)) if m else None
    exp = int(m.group(2)) if m else None
    meta = json.loads((OUT / f"{name}.json").read_text())
    cycles = {
        "logistic_regression": {"cpu_style": 9, "specialized_engine": 3, "explanation": "4 MACs sequentially vs a dedicated dot-product block."},
        "decision_tree": {"cpu_style": 12, "specialized_engine": 4, "explanation": "Sequential compare/branch traversal vs a dedicated tree path."},
        "random_forest": {"cpu_style": 60, "specialized_engine": 5, "explanation": "Five trees sequentially vs five tree engines in parallel + vote."},
        "mlp_classifier": {"cpu_style": 61, "specialized_engine": 8, "explanation": "Dense MACs sequentially vs parallel hidden-neuron MAC blocks + ReLU."},
    }[name]
    result = {
        "ok": rp.returncode == 0 and pred == exp,
        "model": name, "prediction": pred, "expected": exp,
        "sv_output": text.strip(), "train_accuracy": meta["train_accuracy"],
        "hardware": meta["hardware"], "cycles": cycles,
        "speedup_est": cycles["cpu_style"] / cycles["specialized_engine"],
    }
    (OUT / f"inference_{name}.json").write_text(json.dumps(result, indent=2))
    return result

names = list(MODELS) if args.model == "all" else [args.model]
results = [one(n) for n in names]
(OUT / "inference_summary.json").write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2))
raise SystemExit(0 if all(r["ok"] for r in results) else 1)
