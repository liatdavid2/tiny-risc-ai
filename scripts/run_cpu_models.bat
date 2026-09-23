@echo off
python python\train_models.py
if errorlevel 1 exit /b 1
python python\run_tinyrisc_cpu_inference.py
