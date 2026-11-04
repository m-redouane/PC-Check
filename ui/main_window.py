import time
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                             QFrame, QScrollArea, QSizePolicy, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal, QRectF, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QPen, QFont

from core.hardware import HardwareDetector
from core.analyzer import DiagnosticEngine
from core.report_generator import PDFReportGenerator

# --- Jauge Circulaire Animée ---
class CircularGauge(QWidget):
    def __init__(self, color_hex="#22D3EE", size=80):
        super().__init__()
        self.setFixedSize(size, size)
        self._value = 0.0
        self._color = color_hex

    def get_value(self):
        return self._value

    def set_value(self, val):
        self._value = val
        self.update()

    value = Property(float, get_value, set_value)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        margin = 6
        rect = QRectF(margin, margin, self.width() - margin*2, self.height() - margin*2)
        
        pen_bg = QPen(QColor("#27272A"), 8)
        pen_bg.setCapStyle(Qt.RoundCap)
        painter.setPen(pen_bg)
        painter.drawArc(rect, 0, 360 * 16)
        
        pen_val = QPen(QColor(self._color), 8)
        pen_val.setCapStyle(Qt.RoundCap)
        painter.setPen(pen_val)
        span_angle = int(-self._value * 3.6 * 16)
        painter.drawArc(rect, 90 * 16, span_angle)
        
        painter.setPen(QColor("#FAFAFA"))
        font = QFont("Segoe UI Variable Display", 11, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, f"{int(self._value)}%")


class DiagnosticWorker(QThread):
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

        hw = {"os": os_info, "cpu": cpu, "ram": ram, "gpus": gpus, "disks": disks, "physical_disks": physical_disks}
        self.progress_updated.emit(95, "Génération du bilan de santé...")
        analysis = DiagnosticEngine.run_full_diagnostic(hw)
        time.sleep(0.2)
        
        self.progress_updated.emit(100, "Analyse terminée.")
        self.scan_completed.emit(hw, analysis)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PC Check")
        self.resize(1080, 720)
        self.setMinimumSize(950, 620)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #09090B; }
            QLabel { color: #FAFAFA; font-family: 'Segoe UI Variable Display', 'Segoe UI', system-ui, sans-serif; }
            QFrame#sidebar { background-color: #111113; border-right: 1px solid #27272A; }
            QPushButton.nav-btn { background-color: transparent; color: #A1A1AA; font-size: 13px; font-weight: 500; text-align: left; padding: 10px 14px; border-radius: 6px; border: none; }
            QPushButton.nav-btn:hover { background-color: #18181B; color: #FAFAFA; }
            QPushButton.nav-btn[active="true"] { background-color: #27272A; color: #FAFAFA; font-weight: 600; }
            QFrame.panel { background-color: #141417; border-radius: 8px; border: 1px solid #27272A; }
            
            QPushButton#btn_scan { background-color: #FAFAFA; color: #09090B; font-weight: 600; font-size: 13px; padding: 8px 18px; border-radius: 6px; border: none; }
            QPushButton#btn_scan:hover { background-color: #E4E4E7; }
            QPushButton#btn_scan:disabled { background-color: #27272A; color: #71717A; }
            QPushButton#btn_pdf { background-color: #27272A; color: #FAFAFA; font-weight: 600; font-size: 13px; padding: 8px 18px; border-radius: 6px; border: 1px solid #3F3F46; }
            QPushButton#btn_pdf:hover { background-color: #3F3F46; }
            QPushButton#btn_pdf:disabled { background-color: #18181B; color: #52525B; border: 1px solid #27272A; }
        """)

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Panneau latéral
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(210)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 16, 12, 16)
        sidebar_layout.setSpacing(4)

        brand_lbl = QLabel("PC CHECK")
        brand_lbl.setStyleSheet("font-size: 15px; font-weight: 800; letter-spacing: 2px; color: #FAFAFA; padding: 6px 8px 16px 8px;")
        sidebar_layout.addWidget(brand_lbl)

        for text in ["Vue d'ensemble", "Composants", "Diagnostic", "Paramètres"]:
            btn = QPushButton(f"  {text}")
            btn.setProperty("class", "nav-btn")
            if text == "Vue d'ensemble":
                btn.setProperty("active", "true")
            sidebar_layout.addWidget(btn)
            
        sidebar_layout.addStretch()
        version_lbl = QLabel("v0.5.3 • Pro Clean")
        version_lbl.setStyleSheet("color: #52525B; font-size: 11px; padding: 8px;")
        sidebar_layout.addWidget(version_lbl)
        layout.addWidget(sidebar)

        # Contenu principal
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(16)

        top_bar = QHBoxLayout()
        header_title = QLabel("Tableau de bord")
        header_title.setStyleSheet("font-size: 18px; font-weight: 700; color: #FAFAFA;")
        
        self.status_badge = QLabel("Prêt pour l'analyse")
        self.status_badge.setStyleSheet("color: #71717A; font-size: 12px; font-weight: 500; background: #18181B; padding: 4px 10px; border-radius: 4px; border: 1px solid #27272A;")

        self.btn_export = QPushButton("Exporter en PDF")
        self.btn_export.setObjectName("btn_pdf")
        self.btn_export.setEnabled(False)
        self.btn_export.clicked.connect(self.export_pdf)

        self.btn_scan = QPushButton("Lancer le diagnostic")
        self.btn_scan.setObjectName("btn_scan")
        self.btn_scan.clicked.connect(self.start_scan)

        top_bar.addWidget(header_title)
        top_bar.addStretch()
        top_bar.addWidget(self.status_badge)
        top_bar.addWidget(self.btn_export)
        top_bar.addWidget(self.btn_scan)
        content_layout.addLayout(top_bar)

        self.loader_label = QLabel("")
        self.loader_label.setStyleSheet("color: #22D3EE; font-size: 11px; font-weight: 600;")
        content_layout.addWidget(self.loader_label)

        # Grille
        grid = QGridLayout()
        grid.setSpacing(12)

        # CPU
        self.p_cpu = self.create_data_panel("Processeur", "#38BDF8")
        self.lbl_cpu_val = QLabel("Non analysé")
        self.lbl_cpu_val.setStyleSheet("font-size: 13px; font-weight: 600;")
        self.lbl_cpu_sub = QLabel("-")
        self.lbl_cpu_sub.setStyleSheet("color: #A1A1AA; font-size: 12px;")
        self.p_cpu.layout().addWidget(self.lbl_cpu_val)
        self.p_cpu.layout().addWidget(self.lbl_cpu_sub)
        self.p_cpu.layout().addStretch()
        grid.addWidget(self.p_cpu, 0, 0)

        # RAM
        self.p_ram = self.create_data_panel("Mémoire RAM", "#22D3EE")
        ram_h_layout = QHBoxLayout()
        ram_text_layout = QVBoxLayout()
        self.lbl_ram_val = QLabel("Non analysé")
        self.lbl_ram_val.setStyleSheet("font-size: 13px; font-weight: 600;")
        self.lbl_ram_sub = QLabel("-")
        self.lbl_ram_sub.setStyleSheet("color: #A1A1AA; font-size: 12px;")
        ram_text_layout.addWidget(self.lbl_ram_val)
        ram_text_layout.addWidget(self.lbl_ram_sub)
        ram_text_layout.addStretch()
        
        self.gauge_ram = CircularGauge(color_hex="#22D3EE", size=70)
        ram_h_layout.addLayout(ram_text_layout)
        ram_h_layout.addStretch()
        ram_h_layout.addWidget(self.gauge_ram)
        self.p_ram.layout().addLayout(ram_h_layout)
        grid.addWidget(self.p_ram, 0, 1)

        # GPU (Conteneur dynamique propre sans code HTML brut)
        self.p_gpu = self.create_data_panel("Carte Graphique", "#F43F5E")
        self.gpu_container_layout = QVBoxLayout()
        self.gpu_container_layout.setContentsMargins(0, 0, 0, 0)
        self.gpu_container_layout.setSpacing(6)
        
        init_gpu_lbl = QLabel("Non analysé")
        init_gpu_lbl.setStyleSheet("color: #A1A1AA; font-size: 12px;")
        self.gpu_container_layout.addWidget(init_gpu_lbl)
        
        self.p_gpu.layout().addLayout(self.gpu_container_layout)
        self.p_gpu.layout().addStretch()
        grid.addWidget(self.p_gpu, 1, 0)

        # DISQUE
        self.p_disk = self.create_data_panel("Stockage Principal", "#A855F7")
        disk_h_layout = QHBoxLayout()
        disk_text_layout = QVBoxLayout()
        self.lbl_disk_val = QLabel("Non analysé")
        self.lbl_disk_val.setStyleSheet("font-size: 13px; font-weight: 600;")
        self.lbl_disk_sub = QLabel("-")
        self.lbl_disk_sub.setStyleSheet("color: #A1A1AA; font-size: 12px;")
        disk_text_layout.addWidget(self.lbl_disk_val)
        disk_text_layout.addWidget(self.lbl_disk_sub)
        disk_text_layout.addStretch()
        
        self.gauge_disk = CircularGauge(color_hex="#A855F7", size=70)
        disk_h_layout.addLayout(disk_text_layout)
        disk_h_layout.addStretch()
        disk_h_layout.addWidget(self.gauge_disk)
        self.p_disk.layout().addLayout(disk_h_layout)
        grid.addWidget(self.p_disk, 1, 1)

        content_layout.addLayout(grid)

        # Rapport Diagnostic
        p_diag = self.create_data_panel("Rapport de Diagnostic", "#FACC15")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.diag_container = QWidget()
        self.diag_layout = QVBoxLayout(self.diag_container)
        self.diag_layout.setContentsMargins(0, 0, 0, 0)
        self.diag_layout.setSpacing(8)
        
        init_msg = QLabel("Cliquez sur « Lancer le diagnostic » pour démarrer le contrôle.")
        init_msg.setStyleSheet("color: #52525B; font-size: 12px;")
        self.diag_layout.addWidget(init_msg)
        
        scroll.setWidget(self.diag_container)
        p_diag.layout().addWidget(scroll)
        content_layout.addWidget(p_diag, stretch=1)

        layout.addWidget(content_frame)

    def create_data_panel(self, title, accent_color):
        panel = QFrame()
        panel.setProperty("class", "panel")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(16, 14, 16, 14)
        p_layout.setSpacing(8)
        
        t_row = QHBoxLayout()
        t_row.setContentsMargins(0,0,0,0)
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {accent_color}; font-size: 10px;")
        t_lbl = QLabel(title.upper())
        t_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #A1A1AA; letter-spacing: 1px;")
        t_row.addWidget(dot)
        t_row.addWidget(t_lbl)
        t_row.addStretch()
        p_layout.addLayout(t_row)
        return panel

    def start_scan(self):
        self.btn_scan.setEnabled(False)
        self.btn_export.setEnabled(False)
        self.btn_scan.setText("Analyse...")
        
        self.gauge_ram.set_value(0)
        self.gauge_disk.set_value(0)

        self.worker = DiagnosticWorker()
        self.worker.progress_updated.connect(self.on_scan_progress)
        self.worker.scan_completed.connect(self.on_scan_finished)
        self.worker.start()

    def on_scan_progress(self, percent, text):
        self.loader_label.setText(f"En cours : {text} ({percent}%)")

    def animate_gauge(self, gauge_widget, target_value):
        anim = QPropertyAnimation(gauge_widget, b"value")
        anim.setDuration(1000)
        anim.setStartValue(0.0)
        anim.setEndValue(float(target_value))
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        if not hasattr(self, '_animations'):
            self._animations = []
        self._animations.append(anim)

    def on_scan_finished(self, hw, analysis):
        self.loader_label.setText("")
        self.last_hw_data = hw
        self.last_analysis_data = analysis
        
        # CPU
        self.lbl_cpu_val.setText(hw['cpu']['name'])
        self.lbl_cpu_sub.setText(f"{hw['cpu']['physical_cores']} Cœurs Physiques\n{hw['cpu']['logical_cores']} Cœurs Logiques")

        # RAM
        ram_brand = f"{hw['ram']['manufacturer'] or ''} {hw['ram']['part_number'] or ''}".strip()
        self.lbl_ram_val.setText(ram_brand if ram_brand else "Mémoire système")
        self.animate_gauge(self.gauge_ram, hw['ram']['percent_used'])
        
        ram_sub = f"{hw['ram']['total_gb']} Go Total\n{hw['ram']['available_gb']} Go libres"
        if hw['ram']['speed_mhz']: ram_sub += f"\n@ {hw['ram']['speed_mhz']} MHz"
        self.lbl_ram_sub.setText(ram_sub)

        # GPU (Nettoyage et affichage structuré avec des widgets natifs)
        while self.gpu_container_layout.count():
            child = self.gpu_container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if hw['gpus']:
            for gpu in hw['gpus']:
                vram = f"{gpu['vram_gb']} Go" if gpu['vram_gb'] else "N/A"
                
                gpu_item_widget = QWidget()
                gpu_item_layout = QVBoxLayout(gpu_item_widget)
                gpu_item_layout.setContentsMargins(0, 2, 0, 2)
                gpu_item_layout.setSpacing(1)
                
                name_lbl = QLabel(gpu['name'])
                name_lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #FAFAFA;")
                
                sub_lbl = QLabel(f"VRAM : {vram} | Pilote : {gpu['driver_version']}")
                sub_lbl.setStyleSheet("font-size: 11px; color: #A1A1AA;")
                
                gpu_item_layout.addWidget(name_lbl)
                gpu_item_layout.addWidget(sub_lbl)
                
                self.gpu_container_layout.addWidget(gpu_item_widget)
        else:
            no_gpu_lbl = QLabel("Aucun GPU détecté.")
            no_gpu_lbl.setStyleSheet("color: #A1A1AA; font-size: 12px;")
            self.gpu_container_layout.addWidget(no_gpu_lbl)

        # Stockage
        pdisk_name = hw['physical_disks'][0]['model'] if hw['physical_disks'] else "Disque principal"
        self.lbl_disk_val.setText(pdisk_name)
        if hw['disks']:
            d = hw['disks'][0]
            self.animate_gauge(self.gauge_disk, d['percent_used'])
            self.lbl_disk_sub.setText(f"Partition {d['mountpoint']}\n{d['free_gb']} Go libres sur {d['total_gb']} Go")

        # Diagnostic
        while self.diag_layout.count():
            child = self.diag_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for report in analysis['reports']:
            row = QFrame()
            row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            row.setStyleSheet("background: #09090B; border: 1px solid #27272A; border-radius: 6px; padding: 6px;")
            r_box = QVBoxLayout(row)
            r_box.setContentsMargins(8, 6, 8, 6)

            lvl = report['level']
            color = "#EF4444" if lvl == "CRITICAL" else ("#F59E0B" if lvl == "WARNING" else "#10B981")

            t_row = QHBoxLayout()
            badge = QLabel(f"● {lvl}")
            badge.setStyleSheet(f"color: {color}; font-weight: 800; font-size: 10px;")
            t_lbl = QLabel(f"<b>{report['category']}</b> : {report['title']}")
            t_lbl.setStyleSheet("font-size: 13px; color: #F4F4F5;")
            
            t_row.addWidget(badge)
            t_row.addWidget(t_lbl)
            t_row.addStretch()
            r_box.addLayout(t_row)

            desc = QLabel(f"{report['description']}\nConseil : {report['recommendation']}")
            desc.setStyleSheet("font-size: 12px; color: #A1A1AA; line-height: 1.4;")
            r_box.addWidget(desc)
            self.diag_layout.addWidget(row)
            
        self.diag_layout.addStretch()

        status = analysis['overall_status']
        border_col = "#059669" if status == "EXCELLENT" else "#D97706" if status == "À SURVEILLER" else "#DC2626"
        self.status_badge.setText(f"État : {status}")
        self.status_badge.setStyleSheet(f"color: #FAFAFA; font-size: 12px; font-weight: 600; background: #27272A; padding: 4px 10px; border-radius: 4px; border-bottom: 2px solid {border_col};")

        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("Relancer")
        self.btn_export.setEnabled(True)

    def export_pdf(self):
        if not hasattr(self, 'last_hw_data'): return
        try:
            path = PDFReportGenerator.generate_report(self.last_hw_data, self.last_analysis_data)
            QMessageBox.information(self, "Export réussi", f"Rapport PDF généré :\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de l'exportation.\n{e}")