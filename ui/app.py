from pathlib import Path
import json, subprocess, sys
from flask import Flask, jsonify, render_template, request

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)
app = Flask(__name__, template_folder="templates", static_folder="static")


def run_process(cmd):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, shell=isinstance(cmd, str))
    return {"ok": p.returncode == 0, "returncode": p.returncode, "output": (p.stdout or "") + (p.stderr or "")}


def load(name):
    p = RESULTS / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/state")
def state():
    return jsonify({
        "models": load("models_summary.json"),
        "cpu": load("cpu_inference_summary.json"),
        "batch": load("batch_benchmark.json"),
    })


@app.post("/api/train")
def train():
    body = request.get_json(silent=True) or {}
    dataset = body.get("dataset", "breast_cancer")
    if dataset not in {"breast_cancer", "iris"}:
        return jsonify({"ok": False, "output": "Unknown dataset"}), 400
    r = run_process([sys.executable, str(ROOT / "python" / "train_models.py"), "--dataset", dataset])
    r["data"] = load("models_summary.json")
    return jsonify(r)


@app.post("/api/cpu-infer-all")
def cpu_infer_all():
    if not (RESULTS / "models_summary.json").exists():
        tr = run_process([sys.executable, str(ROOT / "python" / "train_models.py")])
        if not tr["ok"]:
            return jsonify(tr), 500
    r = run_process([sys.executable, str(ROOT / "python" / "run_tinyrisc_cpu_inference.py")])
    r["data"] = load("cpu_inference_summary.json")
    r["models"] = load("models_summary.json")
    return jsonify(r)


@app.post("/api/batch-infer")
def batch_infer():
    body = request.get_json(silent=True) or {}
    try:
        max_per_class = int(body.get("max_per_class", 25))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "output": "max_per_class must be an integer"}), 400
    max_per_class = max(1, min(max_per_class, 100))
    if not (RESULTS / "training_artifacts.pkl").exists():
        return jsonify({"ok": False, "output": "Train all models first."}), 400
    r = run_process([sys.executable, str(ROOT / "python" / "run_batch_benchmark.py"), "--max-per-class", str(max_per_class)])
    r["data"] = load("batch_benchmark.json")
    return jsonify(r)


@app.post("/api/sv-tests")
def sv_tests():
    if sys.platform.startswith("win"):
        cmd = str(ROOT / "scripts" / "run_sv_tests.bat")
    else:
        cmd = ["sh", str(ROOT / "scripts" / "run_sv_tests.sh")]
    return jsonify(run_process(cmd))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
