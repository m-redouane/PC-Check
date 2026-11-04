# 💻 PC Check — Logiciel de Diagnostic Système pour Windows

![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python)
![Qt](https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt6-green?logo=qt)
![OS](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows)
![License](https://img.shields.io/badge/License-Proprietary-red)

**PC Check** est une application desktop moderne et sobre permettant d'effectuer un bilan complet et compréhensible des composants matériels d'un ordinateur sous Windows.

---

## 🎯 Objectifs du Projet

- **Détection matérielle précise :** Récupération bas niveau des spécifications exactes (Processeur, RAM, GPU, VRAM 64-bit, SSD/HDD).
- **Moteur de diagnostic intelligent :** Analyse contextuelle des données matérielles et génération d'avertissements et de recommandations personnalisées.
- **Interface sombre & moderne :** Dashboard responsive conçu en PySide6 (Qt6) à thème sombre.
- **Privacy-First :** Analyse 100 % locale, aucune donnée personnelle ou télémétrie envoyée vers un serveur externe.

---

## 🛠️ Stack Technique

- **Langage :** Python 3.12+
- **Interface Graphique :** PySide6 (Qt6)
- **Collecte système :** `psutil`, Windows WMI / CIM (`subprocess`), Windows Registry (`winreg`)
- **Diagnostic :** Moteur d'évaluation modulaire orienté règles métier

---

## 📂 Architecture du Projet

```text
PC-Check/
├── core/
│   ├── __init__.py
│   ├── hardware.py      # Module de collecte matérielle (Win32, WMI, Registre)
│   └── analyzer.py      # Moteur de diagnostic & évaluation d'état
├── ui/
│   ├── __init__.py
│   └── main_window.py   # Dashboard graphique PySide6 (Qt6)
├── .gitignore           # Filtres Git (venv, pycache)
├── main.py              # Point d'entrée principal (GUI)
├── main_cli.py          # Script de test CLI / PoC
└── README.md            # Documentation officielle du dépôt
```

---

## 🚀 Installation & Exécution

### Prérequis
- Windows 10 / 11
- Python 3.10 ou supérieur

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
   pip install psutil PySide6
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
- [ ] **V0.5** — Module d'exportation de rapport PDF (ReportLab)
- [ ] **V0.6** — Gestion de la barre de progression & capteurs thermiques
- [ ] **V1.0** — Packaging `.exe` autonome, système de licences et commercialisation

---

## 📄 Licence

Tous droits réservés © 2026 — **PC Check**.