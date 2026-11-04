import time
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                             QFrame, QProgressBar, QScrollArea)
from PySide6.QtCore import Qt, QThread, Signal
from core.hardware import HardwareDetector
from core.analyzer import DiagnosticEngine

class DiagnosticWorker(QThread):
    """Thread secondaire pour exécuter la collecte système sans bloquer l'interface."""
    progress_updated = Signal(int, str)
    scan_completed = Signal(dict, dict)

    def run(self):
        self.progress_updated.emit(15, "Inspection du processeur...")
        os_info = HardwareDetector.get_os_info()
        cpu = HardwareDetector.get_cpu_info()
        time.sleep(0.3)

        self.progress_updated.emit(40, "Analyse de la mémoire RAM...")
        ram = HardwareDetector.get_ram_info()
        time.sleep(0.3)

        self.progress_updated.emit(65, "Détection des cartes graphiques (GPU)...")
        gpus = HardwareDetector.get_gpu_info()
        time.sleep(0.3)

        self.progress_updated.emit(85, "Analyse des unités de stockage...")
        disks = HardwareDetector.get_disks_info()
        physical_disks = HardwareDetector.get_physical_disks()
        time.sleep(0.3)

        hw = {
            "os": os_info,
            "cpu": cpu,
            "ram": ram,
            "gpus": gpus,
            "disks": disks,
            "physical_disks": physical_disks
        }

        self.progress_updated.emit(95, "Génération du bilan de santé...")
        analysis = DiagnosticEngine.run_full_diagnostic(hw)
        time.sleep(0.2)

        self.progress_updated.emit(100, "Analyse terminée.")
        self.scan_completed.emit(hw, analysis)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PC Check")
        self.resize(1080, 700)
        self.setMinimumSize(950, 620)
        
        # Thème sombre sobre, typographie système épurée
        self.setStyleSheet("""
            QMainWindow {
                background-color: #09090B;
            }
            QLabel {
                color: #FAFAFA;
                font-family: 'Segoe UI Variable Display', 'Segoe UI', system-ui, sans-serif;
            }
            QFrame#sidebar {
                background-color: #111113;
                border-right: 1px solid #27272A;
            }
            QPushButton.nav-btn {
                background-color: transparent;
                color: #A1A1AA;
                font-size: 13px;
                font-weight: 500;
                text-align: left;
                padding: 10px 14px;
                border-radius: 6px;
                border: none;
            }
            QPushButton.nav-btn:hover {
                background-color: #18181B;
                color: #FAFAFA;
            }
            QPushButton.nav-btn[active="true"] {
                background-color: #27272A;
                color: #FAFAFA;
                font-weight: 600;
            }
            QFrame.panel {
                background-color: #141417;
                border-radius: 6px;
                border: 1px solid #27272A;
            }
            QProgressBar {
                background-color: #09090B;
                border: 1px solid #27272A;
                border-radius: 3px;
                height: 6px;
            }
            QProgressBar::chunk {
                background-color: #3B82F6;
                border-radius: 2px;
            }
            QPushButton#btn_scan {
                background-color: #FAFAFA;
                color: #09090B;
                font-weight: 600;
                font-size: 13px;
                padding: 8px 18px;
                border-radius: 6px;
                border: none;
            }
            QPushButton#btn_scan:hover {
                background-color: #E4E4E7;
            }
            QPushButton#btn_scan:disabled {
                background-color: #27272A;
                color: #71717A;
            }
        """)

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # -----------------------------------------------------------------
        # 1. PANNEAU LATÉRAL (SIDEBAR)
        # -----------------------------------------------------------------
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(210)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 16, 12, 16)
        sidebar_layout.setSpacing(4)

        brand_lbl = QLabel("PC CHECK")
        brand_lbl.setStyleSheet("font-size: 14px; font-weight: 800; letter-spacing: 2px; color: #FAFAFA; padding: 6px 8px 16px 8px;")
        sidebar_layout.addWidget(brand_lbl)

        self.btn_nav_dashboard = QPushButton("  Vue d'ensemble")
        self.btn_nav_dashboard.setProperty("class", "nav-btn")
        self.btn_nav_dashboard.setProperty("active", "true")
        
        self.btn_nav_hardware = QPushButton("  Composants")
        self.btn_nav_hardware.setProperty("class", "nav-btn")
        
        self.btn_nav_diag = QPushButton("  Diagnostic")
        self.btn_nav_diag.setProperty("class", "nav-btn")
        
        self.btn_nav_settings = QPushButton("  Paramètres")
        self.btn_nav_settings.setProperty("class", "nav-btn")

        sidebar_layout.addWidget(self.btn_nav_dashboard)
        sidebar_layout.addWidget(self.btn_nav_hardware)
        sidebar_layout.addWidget(self.btn_nav_diag)
        sidebar_layout.addWidget(self.btn_nav_settings)
        sidebar_layout.addStretch()

        version_lbl = QLabel("v0.4.3 • Dev Build")
        version_lbl.setStyleSheet("color: #52525B; font-size: 11px; padding: 8px;")
        sidebar_layout.addWidget(version_lbl)

        layout.addWidget(sidebar)

        # -----------------------------------------------------------------
        # 2. ZONE DE CONTENU PRINCIPALE
        # -----------------------------------------------------------------
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(16)

        # En-tête supérieur (Header)
        top_bar = QHBoxLayout()
        header_title = QLabel("Tableau de bord")
        header_title.setStyleSheet("font-size: 18px; font-weight: 700; color: #FAFAFA;")
        
        self.status_badge = QLabel("Prêt pour l'analyse")
        self.status_badge.setStyleSheet("color: #71717A; font-size: 12px; font-weight: 500; background: #18181B; padding: 4px 10px; border-radius: 4px; border: 1px solid #27272A;")

        self.btn_scan = QPushButton("Lancer le diagnostic")
        self.btn_scan.setObjectName("btn_scan")
        self.btn_scan.clicked.connect(self.start_scan)

        top_bar.addWidget(header_title)
        top_bar.addStretch()
        top_bar.addWidget(self.status_badge)
        top_bar.addWidget(self.btn_scan)
        content_layout.addLayout(top_bar)

        # Barre de progression de chargement (Masquée par défaut)
        self.loader_container = QWidget()
        loader_layout = QVBoxLayout(self.loader_container)
        loader_layout.setContentsMargins(0, 0, 0, 0)
        loader_layout.setSpacing(4)
        
        self.loader_label = QLabel("Analyse en cours...")
        self.loader_label.setStyleSheet("color: #A1A1AA; font-size: 11px;")
        self.scan_progress_bar = QProgressBar()
        self.scan_progress_bar.setValue(0)
        self.scan_progress_bar.setTextVisible(False)
        
        loader_layout.addWidget(self.loader_label)
        loader_layout.addWidget(self.scan_progress_bar)
        self.loader_container.setVisible(False)
        content_layout.addWidget(self.loader_container)

        # Grille d'inspection (Panneaux sobres)
        grid = QGridLayout()
        grid.setSpacing(12)

        # Panel CPU
        self.p_cpu = self.create_data_panel("Processeur")
        self.lbl_cpu_val = QLabel("Non analysé")
        self.lbl_cpu_sub = QLabel("-")
        self.lbl_cpu_sub.setStyleSheet("color: #71717A; font-size: 12px;")
        self.p_cpu.layout().addWidget(self.lbl_cpu_val)
        self.p_cpu.layout().addWidget(self.lbl_cpu_sub)
        grid.addWidget(self.p_cpu, 0, 0)

        # Panel RAM
        self.p_ram = self.create_data_panel("Mémoire RAM")
        self.lbl_ram_val = QLabel("Non analysé")
        self.bar_ram = QProgressBar()
        self.lbl_ram_sub = QLabel("-")
        self.lbl_ram_sub.setStyleSheet("color: #71717A; font-size: 12px;")
        self.p_ram.layout().addWidget(self.lbl_ram_val)
        self.p_ram.layout().addWidget(self.bar_ram)
        self.p_ram.layout().addWidget(self.lbl_ram_sub)
        grid.addWidget(self.p_ram, 0, 1)

        # Panel GPU
        self.p_gpu = self.create_data_panel("Carte Graphique")
        self.lbl_gpu_val = QLabel("Non analysé")
        self.lbl_gpu_val.setWordWrap(True)
        self.p_gpu.layout().addWidget(self.lbl_gpu_val)
        grid.addWidget(self.p_gpu, 1, 0)

        # Panel Disque
        self.p_disk = self.create_data_panel("Stockage Principal")
        self.lbl_disk_val = QLabel("Non analysé")
        self.bar_disk = QProgressBar()
        self.lbl_disk_sub = QLabel("-")
        self.lbl_disk_sub.setStyleSheet("color: #71717A; font-size: 12px;")
        self.p_disk.layout().addWidget(self.lbl_disk_val)
        self.p_disk.layout().addWidget(self.bar_disk)
        self.p_disk.layout().addWidget(self.lbl_disk_sub)
        grid.addWidget(self.p_disk, 1, 1)

        content_layout.addLayout(grid)

        # Bilan Diagnostic
        p_diag = self.create_data_panel("Rapport de Diagnostic")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.diag_container = QWidget()
        self.diag_layout = QVBoxLayout(self.diag_container)
        self.diag_layout.setContentsMargins(0, 0, 0, 0)
        self.diag_layout.setSpacing(8)
        
        init_msg = QLabel("Cliquez sur « Lancer le diagnostic » pour démarrer le contrôle système.")
        init_msg.setStyleSheet("color: #52525B; font-size: 12px;")
        self.diag_layout.addWidget(init_msg)
        
        scroll.setWidget(self.diag_container)
        p_diag.layout().addWidget(scroll)
        content_layout.addWidget(p_diag, stretch=1)

        layout.addWidget(content_frame)

    def create_data_panel(self, title):
        panel = QFrame()
        panel.setProperty("class", "panel")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(14, 12, 14, 12)
        p_layout.setSpacing(6)
        
        t_lbl = QLabel(title.upper())
        t_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #71717A; letter-spacing: 0.8px;")
        p_layout.addWidget(t_lbl)
        return panel

    def start_scan(self):
        self.btn_scan.setEnabled(False)
        self.btn_scan.setText("Analyse...")
        self.loader_container.setVisible(True)
        self.scan_progress_bar.setValue(0)

        # Instanciation et lancement du worker thread
        self.worker = DiagnosticWorker()
        self.worker.progress_updated.connect(self.on_scan_progress)
        self.worker.scan_completed.connect(self.on_scan_finished)
        self.worker.start()

    def on_scan_progress(self, percent, text):
        self.scan_progress_bar.setValue(percent)
        self.loader_label.setText(text)

    def on_scan_finished(self, hw, analysis):
        # 1. CPU
        self.lbl_cpu_val.setText(hw['cpu']['name'])
        self.lbl_cpu_sub.setText(f"{hw['cpu']['physical_cores']} Cœurs Physiques / {hw['cpu']['logical_cores']} Cœurs Logiques")

        # 2. RAM
        ram_brand = f"{hw['ram']['manufacturer'] or ''} {hw['ram']['part_number'] or ''}".strip()
        self.lbl_ram_val.setText(ram_brand if ram_brand else "Mémoire système")
        self.bar_ram.setValue(int(hw['ram']['percent_used']))
        ram_sub_text = f"{hw['ram']['total_gb']} Go Total — {hw['ram']['percent_used']}% utilisé ({hw['ram']['available_gb']} Go libres)"
        if hw['ram']['speed_mhz']:
            ram_sub_text += f" @ {hw['ram']['speed_mhz']} MHz"
        self.lbl_ram_sub.setText(ram_sub_text)

        # 3. GPU
        gpu_str = ""
        for gpu in hw['gpus']:
            vram = f"{gpu['vram_gb']} Go" if gpu['vram_gb'] else "N/A"
            gpu_str += f"<b>{gpu['name']}</b> — <span style='color:#71717A;'>VRAM : {vram} | Pilote : {gpu['driver_version']}</span><br>"
        self.lbl_gpu_val.setText(gpu_str if gpu_str else "Aucun GPU détecté.")

        # 4. DISK
        pdisk_name = hw['physical_disks'][0]['model'] if hw['physical_disks'] else "Disque principal"
        self.lbl_disk_val.setText(pdisk_name)
        if hw['disks']:
            d = hw['disks'][0]
            self.bar_disk.setValue(int(d['percent_used']))
            self.lbl_disk_sub.setText(f"Partition {d['mountpoint']} : {d['free_gb']} Go libres sur {d['total_gb']} Go")

        # 5. DIAGNOSTIC LOG
        for i in reversed(range(self.diag_layout.count())): 
            w = self.diag_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        for report in analysis['reports']:
            row = QFrame()
            row.setStyleSheet("background: #09090B; border: 1px solid #27272A; border-radius: 4px; padding: 6px;")
            r_box = QVBoxLayout(row)
            r_box.setContentsMargins(6, 4, 6, 4)

            lvl = report['level']
            color = "#EF4444" if lvl == "CRITICAL" else ("#F59E0B" if lvl == "WARNING" else "#10B981")

            t_row = QHBoxLayout()
            badge = QLabel(f"● {lvl}")
            badge.setStyleSheet(f"color: {color}; font-weight: 700; font-size: 11px;")
            t_lbl = QLabel(f"<b>{report['category']}</b> : {report['title']}")
            t_lbl.setStyleSheet("font-size: 12px; color: #E4E4E7;")
            
            t_row.addWidget(badge)
            t_row.addWidget(t_lbl)
            t_row.addStretch()
            r_box.addLayout(t_row)

            desc = QLabel(f"{report['description']} — <i>Conseil : {report['recommendation']}</i>")
            desc.setStyleSheet("font-size: 11px; color: #71717A;")
            r_box.addWidget(desc)

            self.diag_layout.addWidget(row)

        # Status & Reset UI
        status = analysis['overall_status']
        self.status_badge.setText(f"État : {status}")
        self.status_badge.setStyleSheet("color: #FAFAFA; font-size: 12px; font-weight: 600; background: #27272A; padding: 4px 10px; border-radius: 4px;")

        self.loader_container.setVisible(False)
        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("Relancer le diagnostic")