import sys
import os
import winreg
from importlib import import_module
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTranslator

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
main_window = import_module("main_window")

def lire_langue_installation():
    """Lit le registre Windows pour savoir ce qu'Inno Setup a enregistré"""
    try:
        # On va chercher la clé créée par Inno Setup
        cle = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\PCCheck")
        valeur, _ = winreg.QueryValueEx(cle, "Langue")
        winreg.CloseKey(cle)
        
        # Si l'installateur était en anglais, on retourne "en"
        if valeur == "english":
            return "en"
    except FileNotFoundError:
        pass
    
    # Par défaut (ou si la clé n'existe pas), on reste en français
    return "fr"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 1. On détecte la langue de l'installateur
    langue_choisie = lire_langue_installation()
    
    # 2. Si c'est l'anglais, on charge le fichier de traduction compilé
    if langue_choisie == "en":
        translator = QTranslator()
        # Assure-toi que "en.qm" est généré avec Qt Linguist et placé dans le bon dossier
        if translator.load("en.qm"):
            app.installTranslator(translator)
            
    # 3. Lancement normal de PC Check
    window = main_window.MainWindow()
    window.show()
    sys.exit(app.exec())