@echo off
set MAX_PER_CLASS=%1
if "%MAX_PER_CLASS%"=="" set MAX_PER_CLASS=25
python python\run_batch_benchmark.py --max-per-class %MAX_PER_CLASS%
