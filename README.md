# TinyRISC-AI

A learning project that builds a small RISC-style CPU from digital-logic blocks in SystemVerilog, trains ML models with scikit-learn on the normal computer, then executes **inference as an instruction program inside the simulated CPU**.

## What is new in this version

TinyRISC now has a real **Instruction Memory** and CPU control-flow instructions:

- `BEQ` — branch if equal
- `BNE` — branch if not equal
- `JAL x0,label` — used as an unconditional `JUMP`
- `HALT` — teaching instruction used to stop the simulator

The Program Counter is therefore no longer limited to `PC + 4`. A branch or jump changes the next PC inside the CPU.

For `DecisionTreeClassifier` and `RandomForestClassifier`, the Python side converts the trained sklearn tree into a TinyRISC instruction program. Threshold decisions and the movement to the left/right child are now performed by **SLTI + BNE/JUMP instructions executing inside TinyRISC**. The test harness no longer chooses tree branches.

```text
sklearn tree
     ↓ export nodes
TinyRISC program
     ↓
Instruction Memory
     ↓
 PC → Fetch → Decoder → Compare
 ↑                         ↓
 └──── BEQ / BNE / JUMP ───┘
     ↓
Prediction
```

## Training vs inference

```text
Dataset
   ↓
scikit-learn on host CPU
   ↓
TRAIN
   ↓
export weights / thresholds / tree nodes
   ↓
compile to TinyRISC instructions
   ↓
Instruction Memory
   ↓
TinyRISC SystemVerilog CPU
   ↓
INFERENCE
```

The UI compares the prediction produced by sklearn on the computer with the prediction produced by the TinyRISC CPU.

## CPU learning path

```text
AND → MUX → Register → Counter/PC → Instruction Memory → ALU
    → Register File → Decoder → BEQ/BNE/JUMP → Mini CPU
```

The CPU supports the small instruction subset needed by the demos: integer add, multiply, compare, arithmetic shift, branches and jumps.

## ML models

- **Logistic Regression** — weights + bias compiled to multiply/add/compare instructions
- **Decision Tree** — thresholds + nodes compiled to compare + branch/jump instructions
- **Random Forest** — each tree runs as CPU control flow; votes are accumulated and majority is computed in TinyRISC
- **MLP Classifier** — layer weights/biases compiled to multiply/add/ReLU control flow

Generated instruction-memory images are written to:

```text
generated/logistic_regression.mem
generated/decision_tree.mem
generated/random_forest.mem
generated/mlp_classifier.mem
```

## Run with Docker Compose

Open Docker Desktop and from Windows CMD run:

```cmd
docker compose up --build
```

Open:

```text
http://localhost:8080
```

Press **RUN ALL**. The UI first shows sklearn training accuracy, then loads each model program into TinyRISC Instruction Memory and compares sklearn prediction with the SystemVerilog CPU prediction.

Run everything without the UI:

```cmd
docker compose run --rm tiny-risc-ai sh scripts/run_all.sh
```

Run only CPU block tests:

```cmd
docker compose run --rm tiny-risc-ai sh scripts/run_sv_tests.sh
```

Stop:

```cmd
docker compose down
```

## Important interpretation

TinyRISC is a teaching CPU in simulation, not a physical chip. `cycles` are simulated CPU instruction cycles. They should not be compared directly with host-computer wall-clock milliseconds.

## Two-step UI workflow: training, then batch inference

The custom one-page UI now separates the experiment into two explicit phases:

1. **TRAIN ALL MODELS** — trains Logistic Regression, Decision Tree, Random Forest and MLPClassifier with scikit-learn on the normal host CPU. The UI shows training accuracy and measured training wall-clock time.
2. **RUN BATCH INFERENCE** — the user chooses **Max / class** (1–100). The app selects up to that many examples from each class and runs the *same samples* through:
   - the original scikit-learn model on the host computer;
   - the TinyRISC SystemVerilog CPU, using the exported/quantized model and its Instruction Memory program.

The batch result reports, per model:

- prediction agreement between sklearn and TinyRISC;
- sklearn accuracy and TinyRISC accuracy against the labels;
- mismatch count;
- real sklearn inference wall-clock time;
- TinyRISC total / average / min / max simulated CPU cycles;
- simulator wall-clock time is collected internally but is **not** presented as hardware latency.

For a binary dataset, `Max / class = 25` means at most 25 class-0 examples + 25 class-1 examples = up to 50 inference samples.

### Run with Docker Compose

```cmd
docker compose up --build
```

Open:

```text
http://localhost:8080
```

Then click **1. TRAIN ALL MODELS**, set **Max / class**, and click **2. RUN BATCH INFERENCE**.
