# TinyRISC-AI

A beginner-friendly, CPU-only project that starts with digital-logic building blocks, combines them into a small RISC-style CPU, and adds a custom **int8 dot-product AI accelerator**.

The complete project now runs inside **Docker** with **Docker Compose**. You do not need to install Python, Flask, scikit-learn, or Icarus Verilog on Windows. Docker Desktop is enough.

## What the project demonstrates

The project is intentionally educational and visual:

```text
Digital logic
   ↓
AND / MUX / Register / Counter
   ↓
ALU + Register File + Decoder
   ↓
Mini CPU
   ↓
Custom AI dot-product accelerator
   ↓
Tiny ML model + CPU-vs-accelerator benchmark
   ↓
Custom HTML/CSS/JavaScript UI
```

The UI explains what each block does and lets you run the hardware tests, train the tiny ML model, and run the benchmark from the browser.

## Stages

1. AND gate
2. 2-to-1 MUX
3. Clocked register
4. Counter / Program Counter concept
5. ALU
6. Register file
7. Instruction decoder
8. Mini CPU
9. int8 dot-product AI accelerator
10. Tiny logistic-regression model
11. CPU-vs-accelerator benchmark + custom web UI

> The CPU is a small RISC-style educational CPU. It is not a complete RISC-V implementation.

## Repository layout

```text
stages/       Step-by-step SystemVerilog exercises
rtl/          Reusable hardware modules
tb/           Extra SystemVerilog testbenches
python/       ML training and benchmark scripts
ui/           Custom Flask + HTML/CSS/JS educational dashboard
scripts/      Windows and Linux/Docker launchers
results/      Generated model/benchmark output
Dockerfile    Container image
docker-compose.yml
```

# Run with Docker Compose on Windows CMD

## 1. Prerequisite

Install and start Docker Desktop. Then open CMD and check:

```cmd
docker --version
docker compose version
```

## 2. Go to the repository

```cmd
cd C:\Users\YOUR_USER\Documents\GitHub\tiny-risc-ai
```

## 3. Build and start everything

```cmd
docker compose up --build
```

The first build installs Python packages and Icarus Verilog inside the container.

Open:

```text
http://localhost:8080
```

That is the custom educational UI.

## 4. Run in the background

```cmd
docker compose up -d --build
```

Check status:

```cmd
docker compose ps
```

View logs:

```cmd
docker compose logs -f
```

Stop the project:

```cmd
docker compose down
```

## Run tests from CMD through Docker

All SystemVerilog tests:

```cmd
docker compose run --rm tiny-risc-ai sh scripts/run_sv_tests.sh
```

Expected final line:

```text
ALL SYSTEMVERILOG TESTS PASSED.
```

Train the tiny ML model and run the benchmark:

```cmd
docker compose run --rm tiny-risc-ai sh scripts/run_ai_demo.sh
```

Run everything:

```cmd
docker compose run --rm tiny-risc-ai sh scripts/run_all.sh
```

The generated JSON files are written to the local `results` directory because Docker Compose mounts it into the container.

## What runs where?

```text
Windows PC
   ↓
Docker Desktop
   ↓
Docker Compose
   ↓
TinyRISC-AI container
   ├── Icarus Verilog → SystemVerilog simulation + verification
   ├── Python         → ML training + benchmark
   ├── Flask          → backend API
   └── HTML/CSS/JS    → custom explanatory UI
             ↓
        localhost:8080
```

No GPU is required. The Docker container runs entirely on the host CPU.

## AI part

`python/train_model.py` creates a small 4-feature binary-classification dataset, trains logistic regression, and quantizes the model weights/sample to int8.

The accelerator computes a hardware-friendly dot product:

```text
score = x0*w0 + x1*w1 + x2*w2 + x3*w3 + bias
prediction = score >= 0
```

The SystemVerilog accelerator computes the four int8 multiply-accumulate terms. The Python benchmark compares this against a simple educational CPU execution model.

**Important:** cycle counts are architectural estimates for learning. They are not measurements of physical silicon latency or power.
