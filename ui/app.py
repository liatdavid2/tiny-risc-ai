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
    })


@app.post("/api/train")
def train():
    r = run_process([sys.executable, str(ROOT / "python" / "train_models.py")])
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


@app.post("/api/infer")
def infer():
    model = (request.get_json(silent=True) or {}).get("model", "logistic_regression")
    allowed = {"logistic_regression", "decision_tree", "random_forest", "mlp_classifier"}
    if model not in allowed:
        return jsonify({"ok": False, "output": "Unknown model"}), 400
    if not (RESULTS / "models_summary.json").exists():
        run_process([sys.executable, str(ROOT / "python" / "train_models.py")])
    r = run_process([sys.executable, str(ROOT / "python" / "run_hardware_inference.py"), "--model", model])
    r["data"] = load(f"inference_{model}.json")
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
