@echo off
setlocal
cd /d "%~dp0"
pyinstaller --onefile --windowed --name HH_Vacancy_Analyzer main.py
echo.
echo Build finished. EXE: dist\HH_Vacancy_Analyzer.exe
pause
