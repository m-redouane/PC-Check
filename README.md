# 💻 PC Check — Logiciel de Diagnostic Système pour Windows

![Version](https://img.shields.io/badge/Version-1.0.6-blue)
![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python)
![Qt](https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt6-green?logo=qt)
![OS](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows)
![License](https://img.shields.io/badge/License-Proprietary-red)

**PC Check** est une application desktop moderne et sobre permettant d'effectuer un bilan complet et compréhensible des composants matériels d'un ordinateur sous Windows.

---

## 🎯 Objectifs du Projet

- **Détection matérielle précise :** Récupération bas niveau des spécifications exactes (Processeur, RAM, GPU, VRAM 64-bit, SSD/HDD).
- **Surveillance en direct (Live Monitoring) :** Lecture en temps réel des sondes matérielles (Températures, Tensions, Charges, Fréquences) grâce au moteur matériel LibreHardwareMonitor intégré.
- **Moteur de diagnostic intelligent :** Analyse contextuelle des données matérielles et génération d'avertissements et de recommandations personnalisées.
- **Interface sombre & moderne :** Dashboard responsive conçu en PySide6 (Qt6) à thème sombre, incluant un explorateur matériel arborescent complet.
- **Rapports PDF :** Génération en un clic d'un bilan de santé matériel professionnel.
- **Privacy-First :** Analyse 100 % locale, aucune donnée personnelle ou télémétrie envoyée vers un serveur externe.

---

## 🛠️ Stack Technique

- **Langage :** Python 3.12+
- **Interface Graphique :** PySide6 (Qt6)
- **Collecte système :** `psutil`, Windows WMI / CIM (`subprocess`), Windows Registry (`winreg`)
- **Lecture des Sondes (Capteurs) :** `LibreHardwareMonitorLib.dll` interfacé via `pythonnet`
- **Génération PDF :** `reportlab`
- **Diagnostic :** Moteur d'évaluation modulaire orienté règles métier

---

## 📂 Architecture du Projet

```text
PC-Check/
├── core/
│   ├── __init__.py
│   ├── LibreHardwareMonitorLib.dll # Moteur matériel embarqué (.NET)
│   ├── hardware.py         # Module de collecte matérielle statique (Win32, WMI, Registre)
│   ├── sensors.py          # Collecte dynamique des sondes en direct (LHM)
│   ├── analyzer.py         # Moteur de diagnostic & évaluation d'état
│   ├── report_generator.py # Générateur de rapports professionnels (PDF)
│   └── logger.py           # Système centralisé de journalisation
├── ui/
│   ├── __init__.py
│   └── main_window.py      # Dashboard graphique PySide6 avec QTreeWidget matériel
├── .gitignore              # Filtres Git (venv, pycache)
├── main.py                 # Point d'entrée principal (GUI)
├── main_cli.py             # Script de test CLI / PoC
└── README.md               # Documentation officielle du dépôt
```

---

## 🚀 Installation & Exécution

### Prérequis
- Windows 10 / 11
- Python 3.10 ou supérieur
- **Privilèges Administrateur** (Recommandé pour la lecture complète des capteurs de température et de tension du CPU/GPU).

### Étapes d'installation

1. **Cloner le dépôt privé :**
   ```bash
   git clone https://github.com/m-redouane/PC-Check.git
   cd PC-Check
   ```

2. **Créer et activer l'environnement virtuel :**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Installer les dépendances :**
   ```powershell
   pip install psutil PySide6 pythonnet reportlab
   ```

4. **Lancer l'application :**
   ```powershell
   python main.py
   ```

---

## 📌 Feuille de Route (Roadmap)

- [x] **V0.1** — Preuve de concept (CLI, détection CPU/RAM)
- [x] **V0.2** — Détection GPU (VRAM 64-bit) & Stockage physique
- [x] **V0.3** — Moteur de diagnostic contextuel & règles métier
- [x] **V0.4** — Dashboard GUI sombre avec PySide6
- [x] **V0.5** — Module d'exportation de rapport PDF (ReportLab)
- [x] **V0.6** — Gestion des capteurs matériels en direct avec LibreHardwareMonitor (LHM)
- [x] **V1.0.6** — Explorateur matériel arborescent complet (Tree View - Températures, Voltages, Loads)
- [ ] **V1.1** — Packaging `.exe` autonome (PyInstaller), système de licences et commercialisation

---

## 📄 Licence

Tous droits réservés © 2026 — **PC Check**.