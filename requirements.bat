@echo off
setlocal

REM Se placer dans le dossier du .bat
cd /d "%~dp0"

REM Vérifier la venv
if not exist "env\Scripts\activate.bat" (
    echo ERREUR : venv "env" introuvable
    pause
    exit /b 1
)

REM Créer assets si absent
if not exist "assets" (
    mkdir assets
)

REM Activer la venv
call env\Scripts\activate.bat

REM Freeze via PowerShell (UTF-8 GARANTI)
powershell -NoProfile -Command ^
    "pip freeze | Out-File -FilePath 'assets\requirements.txt' -Encoding UTF8"

REM Désactiver la venv
deactivate

echo requirements.txt genere correctement (UTF-8).
pause
