from pathlib import Path
import json
import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)

X, y = make_classification(n_samples=500, n_features=4, n_informative=4,
                           n_redundant=0, random_state=7, class_sep=1.4)
model = LogisticRegression(max_iter=1000, random_state=7)
model.fit(X, y)
acc = accuracy_score(y, model.predict(X))

# Symmetric int8 quantization for a small hardware demo.
x_scale = max(np.max(np.abs(X)), 1e-9) / 100.0
w = model.coef_[0]
w_scale = max(np.max(np.abs(w)), 1e-9) / 100.0
q_w = np.clip(np.round(w / w_scale), -127, 127).astype(int)
# Convert floating bias to the same integer accumulator scale.
q_bias = int(round(model.intercept_[0] / (x_scale * w_scale)))

sample = X[0]
q_x = np.clip(np.round(sample / x_scale), -127, 127).astype(int)
int_score = int(np.dot(q_x, q_w) + q_bias)
int_pred = int(int_score >= 0)

payload = {
    "float_accuracy_train": float(acc),
    "weights_float": w.tolist(),
    "bias_float": float(model.intercept_[0]),
    "weights_int8": q_w.tolist(),
    "bias_int32": q_bias,
    "input_sample_float": sample.tolist(),
    "input_sample_int8": q_x.tolist(),
    "expected_prediction": int(y[0]),
    "quantized_prediction": int_pred,
    "quantized_score": int_score,
    "x_scale": float(x_scale),
    "w_scale": float(w_scale)
}
(OUT / "model.json").write_text(json.dumps(payload, indent=2))
print("Saved results/model.json")
print(f"Train accuracy: {acc:.3f}")
print(f"Quantized sample prediction: {int_pred} (expected {int(y[0])})")
