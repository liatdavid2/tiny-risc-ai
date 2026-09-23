# TinyRISC-AI

A learning project that builds a small RISC-style CPU from digital-logic blocks in SystemVerilog, trains scikit-learn models on **real built-in datasets**, then executes inference as an instruction program inside the simulated TinyRISC CPU.

## Datasets — no synthetic data

The UI offers only two real, well-known scikit-learn datasets:

- **Breast Cancer Wisconsin** — binary classification. The original dataset has 569 rows and 30 features. TinyRISC v1 uses four real features so the same 4-input teaching CPU can run both datasets: mean radius, mean texture, mean perimeter and mean area.
- **Iris** — 150 rows, all 4 original features, 3 classes: setosa, versicolor and virginica.

Both datasets come directly from `sklearn.datasets`; no CSV download is required.

## Experiment flow

```text
Choose real dataset
        ↓
TRAIN ALL MODELS on normal computer
        ↓
scikit-learn
  Logistic Regression
  Decision Tree
  Random Forest
  MLPClassifier
        ↓
Export / quantize model parameters
        ↓
Compile model to TinyRISC instructions
        ↓
Instruction Memory
        ↓
RUN BATCH INFERENCE
        ↓
Same held-out test samples
   ┌───────────────┴───────────────┐
   ↓                               ↓
sklearn / host CPU          TinyRISC / SystemVerilog
   ↓                               ↓
predictions + ms            predictions + CPU cycles
   └───────────────┬───────────────┘
                   ↓
        accuracy + agreement
```

Training uses a stratified 70/30 train/test split. Batch inference is run on the **held-out test set**, not the training samples.

## Batch selection

The UI has a `Max / class` field. For example:

- Breast Cancer, `25` → up to 25 malignant + 25 benign = 50 samples.
- Iris, `25` → up to 25 setosa + 25 versicolor + 25 virginica = 75 samples.

The exact same batch is sent to sklearn and to TinyRISC.

## CPU LEGO path

```text
AND → MUX → Register → Counter/PC → Instruction Memory → ALU
    → Register File → Decoder → BEQ/BNE/JUMP → Tiny CPU
```

TinyRISC includes instruction memory and CPU control flow. Decision Tree and Random Forest branches execute inside the CPU using compare + `BEQ/BNE/JUMP`. Iris multiclass inference is supported: Logistic Regression and MLP calculate class scores and perform argmax; Random Forest counts votes by class.

## Models

- **Logistic Regression** — class score dot products + sign/argmax.
- **Decision Tree** — threshold comparisons + CPU branches.
- **Random Forest** — several tree programs + class voting + argmax.
- **MLP Classifier** — matrix multiply + ReLU + output scores + sign/argmax.

## UI workflow

The custom one-page UI intentionally has two main buttons:

1. **TRAIN ALL MODELS** — choose Breast Cancer or Iris, train all four sklearn models and show held-out test accuracy + training time.
2. **RUN BATCH INFERENCE** — choose maximum samples per class and compare sklearn predictions against TinyRISC predictions.

Per model, the UI shows:

- sklearn test accuracy;
- TinyRISC batch accuracy;
- sklearn ↔ TinyRISC prediction agreement;
- mismatch count;
- real sklearn inference wall-clock time;
- TinyRISC total / average / min / max simulated CPU cycles.

Host milliseconds and TinyRISC cycles are deliberately kept as different units. TinyRISC is a simulated teaching CPU, not a physical chip.

## Run with Docker Compose

Open Docker Desktop. From Windows CMD:

```cmd
docker compose up --build
```

Open:

```text
http://localhost:8080
```

Then:

1. choose **Breast Cancer** or **Iris**;
2. click **TRAIN ALL MODELS**;
3. choose `Max / class`;
4. click **RUN BATCH INFERENCE**.

Run everything from the command line using the default Breast Cancer dataset:

```cmd
docker compose run --rm tiny-risc-ai sh scripts/run_all.sh
```

Train Iris explicitly:

```cmd
docker compose run --rm tiny-risc-ai python python/train_models.py --dataset iris
```

Then run a balanced batch:

```cmd
docker compose run --rm tiny-risc-ai python python/run_batch_benchmark.py --max-per-class 25
```

Run only the SystemVerilog CPU block tests:

```cmd
docker compose run --rm tiny-risc-ai sh scripts/run_sv_tests.sh
```

Stop the app:

```cmd
docker compose down
```

## Architecture LEGO Explorer

After running batch inference, the UI can compare the exact same trained-model workload across several teaching architectures:

- **Base TinyRISC** — the SystemVerilog CPU execution measured by the batch benchmark.
- **TinyRISC + 2× MAC** — adds two parallel multiply-accumulate lanes.
- **TinyRISC + 4× MAC** — adds four parallel MAC lanes.
- **TinyRISC + 8× MAC** — optional larger accelerator block.

The base cycle count comes from the real SystemVerilog TinyRISC batch run. Optional MAC blocks use a transparent architecture-cycle model: scalar `MUL + ADD` MAC terms are replaced by `ceil(MAC terms / lanes)` accelerator cycles. Decision Tree and Random Forest do not contain matrix/dot-product MAC work, so the MAC block intentionally does not speed them up.

These values are **simulated/projected architecture cycles, not physical wall-clock chip latency**. Prediction accuracy/agreement is unchanged because the trained model and quantized arithmetic are unchanged.


## Architecture LEGO selector

The UI keeps **Base TinyRISC** as a fixed reference architecture. Use the **ADD ARCHITECTURE** dropdown to add `TinyRISC + 2× MAC`, `+4× MAC`, or `+8× MAC` as separate complete designs. Optional designs can be removed with the `×` button. A single design never stacks multiple MAC widths; each preset represents one logical alternative architecture.
