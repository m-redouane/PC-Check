@echo off
echo Compilation de PC-Check en cours...
pyinstaller --onefile --windowed --uac-admin --name="PC-Check" --icon="assets/logo.ico" --add-data "assets;assets" --add-data "core;core" main.py
echo Compilation terminee ! Le nouvel exe est dans le dossier dist.
pause