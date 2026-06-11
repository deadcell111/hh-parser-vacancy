$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
pyinstaller --onefile --windowed --name HH_Vacancy_Analyzer main.py
Write-Host ""
Write-Host "Build finished. EXE: dist\HH_Vacancy_Analyzer.exe"
