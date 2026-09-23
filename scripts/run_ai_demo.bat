@echo off
setlocal
cd /d "%~dp0.."
python python\train_model.py || exit /b 1
python python\benchmark.py || exit /b 1
echo.
echo AI demo finished. Results are in the results folder.
