from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QPushButton, QFrame)
from PySide6.QtCore import Qt
from core.hardware import HardwareDetector
from core.analyzer import DiagnosticEngine

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PC Check — Dashboard Système")
        self.resize(1000, 700)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0F172A;
            }
            QLabel {
                color: #E2E8F0;
                font-family: 'Segoe UI', sans-serif;
            }
            QFrame.card {
                background-color: #1E293B;
                border-radius: 8px;
                border: 1px solid #334155;
            }
            QPushButton#btn_scan {
                background-color: #2563EB;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 24px;
                border-radius: 6px;
                border: none;
            }
            QPushButton#btn_scan:hover {
                background-color: #1D4ED8;
            }
        """)

        self.init_ui()

    def create_card(self, title):
        card = QFrame()
        card.setProperty("class", "card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        
        header = QLabel(title)
        header.setStyleSheet("font-size: 15px; font-weight: bold; color: #38BDF8;")
        layout.addWidget(header)
        
        content = QLabel("En attente d'analyse...")
        content.setWordWrap(True)
        content.setStyleSheet("font-size: 13px; color: #94A3B8; margin-top: 6px;")
        layout.addWidget(content)
        
        return card, content

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("PC Check")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #F8FAFC;")
        
        self.status_badge = QLabel("Prêt pour le diagnostic")
        self.status_badge.setStyleSheet("color: #94A3B8; font-size: 14px; font-weight: 500;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_badge)
        main_layout.addLayout(header_layout)

        # Grille des composants
        grid_layout = QGridLayout()
        grid_layout.setSpacing(16)

        self.card_cpu, self.lbl_cpu = self.create_card("Processeur (CPU)")
        self.card_ram, self.lbl_ram = self.create_card("Mémoire (RAM)")
        self.card_gpu, self.lbl_gpu = self.create_card("Graphiques (GPU)")
        self.card_disk, self.lbl_disk = self.create_card("Stockage & Disques")

        grid_layout.addWidget(self.card_cpu, 0, 0)
        grid_layout.addWidget(self.card_ram, 0, 1)
        grid_layout.addWidget(self.card_gpu, 1, 0)
        grid_layout.addWidget(self.card_disk, 1, 1)
        main_layout.addLayout(grid_layout)

        # Bilan Diagnostic
        self.card_diag, self.lbl_diag = self.create_card("Résultats du Diagnostic")
        main_layout.addWidget(self.card_diag, stretch=1)

        # Bouton d'action
        btn_layout = QHBoxLayout()
        self.btn_scan = QPushButton("Lancer le diagnostic")
        self.btn_scan.setObjectName("btn_scan")
        self.btn_scan.clicked.connect(self.run_scan)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_scan)
        main_layout.addLayout(btn_layout)

    def run_scan(self):
        self.status_badge.setText("Analyse en cours...")
        
        hw = {
            "os": HardwareDetector.get_os_info(),
            "cpu": HardwareDetector.get_cpu_info(),
            "ram": HardwareDetector.get_ram_info(),
            "gpus": HardwareDetector.get_gpu_info(),
            "disks": HardwareDetector.get_disks_info(),
            "physical_disks": HardwareDetector.get_physical_disks()
        }
        analysis = DiagnosticEngine.run_full_diagnostic(hw)

        self.status_badge.setText(f"État global : {analysis['overall_status']}")

        # Affichage CPU
        self.lbl_cpu.setText(f"<b>Modèle :</b> {hw['cpu']['name']}<br><b>Cœurs :</b> {hw['cpu']['physical_cores']} Physiques / {hw['cpu']['logical_cores']} Logiques")
        
        # Affichage RAM avec Marque, Modèle, Fréquence et Barrettes
        ram_detail = ""
        brand_parts = []
        if hw['ram']['manufacturer']:
            brand_parts.append(hw['ram']['manufacturer'])
        if hw['ram']['part_number']:
            brand_parts.append(hw['ram']['part_number'])
            
        if brand_parts:
            ram_detail += f"<b>Modèle :</b> {' '.join(brand_parts)}<br>"
            
        ram_detail += f"<b>Capacité :</b> {hw['ram']['total_gb']} Go<br>"
        ram_detail += f"<b>Utilisation :</b> {hw['ram']['percent_used']}% (Libre : {hw['ram']['available_gb']} Go)<br>"
        if hw['ram']['speed_mhz']:
            ram_detail += f"<b>Fréquence :</b> {hw['ram']['speed_mhz']} MHz ({hw['ram']['slots_used']} barrette(s))"
        self.lbl_ram.setText(ram_detail)

        # Affichage GPU
        gpu_text = ""
        for gpu in hw['gpus']:
            vram = f"{gpu['vram_gb']} Go" if gpu['vram_gb'] is not None else "N/A"
            gpu_text += f"• <b>{gpu['name']}</b><br>&nbsp;&nbsp;VRAM : {vram} | Pilote : {gpu['driver_version']}<br>"
        self.lbl_gpu.setText(gpu_text if gpu_text else "Aucun GPU détecté.")

        # Affichage Stockage (Modèle SSD physique + Partitions)
        disk_text = ""
        if hw['physical_disks']:
            for pdisk in hw['physical_disks']:
                disk_text += f"• <b>{pdisk['model']}</b> ({pdisk['size_gb']} Go)<br>"
        for disk in hw['disks']:
            disk_text += f"&nbsp;&nbsp; Partition <b>{disk['mountpoint']}</b> : {disk['free_gb']} Go libres sur {disk['total_gb']} Go<br>"
        self.lbl_disk.setText(disk_text)

        # Bilan Diagnostic
        diag_text = ""
        for report in analysis['reports']:
            color = "#EF4444" if report['level'] == "CRITICAL" else ("#F59E0B" if report['level'] == "WARNING" else "#10B981")
            diag_text += f"<span style='color:{color}; font-weight:bold;'>[{report['level']}] {report['category']}</span> : {report['title']}<br>"
            diag_text += f"<i>{report['description']}</i><br><b>Conseil :</b> {report['recommendation']}<br><br>"
        self.lbl_diag.setText(diag_text)