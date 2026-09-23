#!/usr/bin/env sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
BUILD="$ROOT/build"
mkdir -p "$BUILD"

run_test() {
  name="$1"
  shift
  echo ""
  echo "===== $name ====="
  iverilog -g2012 -Wall -o "$BUILD/test.out" "$@"
  vvp "$BUILD/test.out"
}

run_test "01 AND gate" \
  "$ROOT/stages/01_and_gate/design.sv" \
  "$ROOT/stages/01_and_gate/testbench.sv"

run_test "02 MUX" \
  "$ROOT/stages/02_mux/design.sv" \
  "$ROOT/stages/02_mux/testbench.sv"

run_test "03 Register" \
  "$ROOT/rtl/register.sv" \
  "$ROOT/stages/03_register/testbench.sv"

run_test "04 Counter" \
  "$ROOT/rtl/counter.sv" \
  "$ROOT/stages/04_counter/testbench.sv"

run_test "05 ALU" \
  "$ROOT/rtl/alu.sv" \
  "$ROOT/stages/05_alu/testbench.sv"

run_test "06 Register File" \
  "$ROOT/rtl/register_file.sv" \
  "$ROOT/stages/06_register_file/testbench.sv"

run_test "07 Decoder" \
  "$ROOT/rtl/decoder.sv" \
  "$ROOT/stages/07_decoder/testbench.sv"

run_test "08 Mini CPU" \
  "$ROOT/rtl/alu.sv" \
  "$ROOT/rtl/register_file.sv" \
  "$ROOT/rtl/decoder.sv" \
  "$ROOT/rtl/ai_accelerator.sv" \
  "$ROOT/rtl/cpu.sv" \
  "$ROOT/stages/08_mini_cpu/testbench.sv"

run_test "09 AI Accelerator" \
  "$ROOT/rtl/ai_accelerator.sv" \
  "$ROOT/tb/ai_accelerator_tb.sv"

echo ""
echo "ALL SYSTEMVERILOG TESTS PASSED."
