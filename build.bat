@echo off
echo Compilation de PC-Check en cours...
python -m PyInstaller --onefile --windowed --name="PC-Check" --icon="assets/logo.ico" --add-data "assets;assets" --add-data "core;core" --add-data "en.qm;." main.py
if %errorlevel% neq 0 (
    echo ERREUR : La compilation a echoue !
    pause
    exit /b %errorlevel%
)
echo Compilation terminee ! Le nouvel exe est dans le dossier dist.
pause