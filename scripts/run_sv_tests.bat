@echo off
setlocal
where iverilog >nul 2>nul
if errorlevel 1 (
  echo ERROR: iverilog was not found in PATH.
  echo Install Icarus Verilog first, then reopen CMD.
  exit /b 1
)

cd /d "%~dp0.."
if not exist build mkdir build

echo === 01 AND ===
iverilog -g2012 -o build\t01 stages\01_and_gate\design.sv stages\01_and_gate\testbench.sv && vvp build\t01 || exit /b 1

echo === 02 MUX ===
iverilog -g2012 -o build\t02 stages\02_mux\design.sv stages\02_mux\testbench.sv && vvp build\t02 || exit /b 1

echo === 03 REGISTER ===
iverilog -g2012 -o build\t03 rtl\register.sv stages\03_register\testbench.sv && vvp build\t03 || exit /b 1

echo === 04 COUNTER ===
iverilog -g2012 -o build\t04 rtl\counter.sv stages\04_counter\testbench.sv && vvp build\t04 || exit /b 1

echo === 05 ALU ===
iverilog -g2012 -o build\t05 rtl\alu.sv stages\05_alu\testbench.sv && vvp build\t05 || exit /b 1

echo === 06 REGISTER FILE ===
iverilog -g2012 -o build\t06 rtl\register_file.sv stages\06_register_file\testbench.sv && vvp build\t06 || exit /b 1

echo === 07 DECODER ===
iverilog -g2012 -o build\t07 rtl\decoder.sv stages\07_decoder\testbench.sv && vvp build\t07 || exit /b 1

echo === 08 MINI CPU ===
iverilog -g2012 -o build\t08 rtl\alu.sv rtl\register_file.sv rtl\decoder.sv rtl\ai_accelerator.sv rtl\instruction_memory.sv rtl\cpu.sv stages\08_mini_cpu\testbench.sv && vvp build\t08 || exit /b 1

echo === AI ACCELERATOR ===
iverilog -g2012 -o build\tai rtl\ai_accelerator.sv tb\ai_accelerator_tb.sv && vvp build\tai || exit /b 1

echo.
echo ALL SYSTEMVERILOG TESTS PASSED.
