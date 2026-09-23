@echo off
python python\train_models.py
if errorlevel 1 exit /b 1
python python\run_hardware_inference.py --model all
