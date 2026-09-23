@echo off
setlocal
cd /d "%~dp0.."
call scripts\run_sv_tests.bat || exit /b 1
call scripts\run_ai_demo.bat || exit /b 1
echo.
echo Everything finished successfully.
