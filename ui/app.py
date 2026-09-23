from pathlib import Path
import json
import subprocess
import sys

from flask import Flask, jsonify, render_template

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

app = Flask(__name__, template_folder="templates", static_folder="static")


def run_process(cmd):
    p = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        shell=isinstance(cmd, str),
    )
    return {
        "ok": p.returncode == 0,
        "returncode": p.returncode,
        "output": (p.stdout or "") + (p.stderr or ""),
    }


def load_json(name):
    path = RESULTS / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/results")
def results():
    return jsonify({
        "model": load_json("model.json"),
        "benchmark": load_json("benchmark.json"),
    })


@app.post("/api/train")
def train():
    result = run_process([sys.executable, str(ROOT / "python" / "train_model.py")])
    result["data"] = load_json("model.json")
    return jsonify(result)


@app.post("/api/benchmark")
def benchmark():
    result = run_process([sys.executable, str(ROOT / "python" / "benchmark.py")])
    result["data"] = load_json("benchmark.json")
    return jsonify(result)


@app.post("/api/sv-tests")
def sv_tests():
    if sys.platform.startswith("win"):
        result = run_process(str(ROOT / "scripts" / "run_sv_tests.bat"))
    else:
        result = run_process(["sh", str(ROOT / "scripts" / "run_sv_tests.sh")])
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
