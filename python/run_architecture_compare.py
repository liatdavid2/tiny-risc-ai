from pathlib import Path
import argparse, json, math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
MODELS = ["logistic_regression", "decision_tree", "random_forest", "mlp_classifier"]


def mac_ops_per_sample(model_name, meta):
    """Number of scalar multiply-accumulate terms in the exported inference graph."""
    ex = meta.get("exported", {})
    if model_name == "logistic_regression":
        W = ex.get("weights_int8", [])
        return sum(len(row) for row in W)
    if model_name == "mlp_classifier":
        W1 = ex.get("w1_int8", [])
        W2 = ex.get("w2_int8", [])
        first = sum(len(row) for row in W1)
        second = sum(len(row) for row in W2)
        return first + second
    return 0


def normalize_architectures(raw):
    archs = []
    seen = set()
    for i, a in enumerate(raw or []):
        try:
            lanes = int(a.get("mac_lanes", 0))
        except Exception:
            lanes = 0
        if lanes not in {0, 2, 4, 8}:
            lanes = 0
        name = str(a.get("name") or ("Base TinyRISC" if lanes == 0 else f"TinyRISC + {lanes}× MAC")).strip()[:40]
        key = (name, lanes)
        if key in seen:
            continue
        seen.add(key)
        archs.append({"id": f"arch_{i}", "name": name, "mac_lanes": lanes})
    if not archs:
        archs = [
            {"id":"base", "name":"Base TinyRISC", "mac_lanes":0},
            {"id":"mac2", "name":"TinyRISC + 2× MAC", "mac_lanes":2},
            {"id":"mac4", "name":"TinyRISC + 4× MAC", "mac_lanes":4},
        ]
    return archs[:6]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--architectures-json", default="[]")
    args = ap.parse_args()

    batch_path = OUT / "batch_benchmark.json"
    if not batch_path.exists():
        raise SystemExit("Run batch inference first.")
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    try:
        raw_arch = json.loads(args.architectures_json)
    except json.JSONDecodeError as e:
        raise SystemExit(f"Invalid architecture JSON: {e}")
    archs = normalize_architectures(raw_arch)

    batch_by = {m["model"]: m for m in batch["models"]}
    model_rows = []
    for model_name in MODELS:
        bm = batch_by[model_name]
        meta = json.loads((OUT / f"{model_name}.json").read_text(encoding="utf-8"))
        mac_ops = mac_ops_per_sample(model_name, meta)
        base = float(bm["cpu_avg_cycles_per_sample"])
        variants = []
        for a in archs:
            lanes = a["mac_lanes"]
            if lanes <= 0 or mac_ops == 0:
                est = base
                saved = 0.0
            else:
                # Current TinyRISC executes each MAC term as MUL + ADD = 2 scalar instructions/cycles.
                # The optional MAC block replaces those 2*MAC scalar cycles with ceil(MAC/lanes)
                # accelerator cycles. Everything else stays at the measured TinyRISC baseline cost.
                scalar_mac_cycles = 2 * mac_ops
                accel_cycles = math.ceil(mac_ops / lanes)
                est = max(1.0, base - scalar_mac_cycles + accel_cycles)
                saved = max(0.0, base - est)
            variants.append({
                "architecture": a["name"],
                "mac_lanes": lanes,
                "avg_cycles": round(est, 2),
                "speedup_vs_base": round(base / est, 3) if est > 0 else None,
                "cycles_saved": round(saved, 2),
            })
        model_rows.append({
            "model": model_name,
            "base_avg_cycles": base,
            "mac_ops_per_sample": mac_ops,
            "agreement": bm["agreement"],
            "tiny_accuracy": bm["cpu_accuracy"],
            "architectures": variants,
        })

    payload = {
        "dataset": batch.get("dataset"),
        "samples": batch.get("samples"),
        "architectures": archs,
        "models": model_rows,
        "method": "Architecture cycle model anchored to the measured TinyRISC batch execution. Base cycles come from the SystemVerilog CPU. Optional parallel-MAC blocks replace scalar MUL+ADD MAC terms with ceil(MACs/lanes) accelerator cycles. Tree/forest models have no MAC terms, so MAC blocks do not speed them up.",
        "important": "These are simulated/projected architecture cycles, not wall-clock hardware latency. Prediction quality is unchanged because the trained model and quantized arithmetic are unchanged.",
    }
    (OUT / "architecture_compare.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
