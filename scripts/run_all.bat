@echo off
call scripts\run_sv_tests.bat
if errorlevel 1 exit /b 1
call scripts\run_models.bat
