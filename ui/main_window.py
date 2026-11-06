import os
import time
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                             QFrame, QScrollArea, QSizePolicy, QMessageBox, 
                             QStackedWidget, QTreeWidget, QTreeWidgetItem, QHeaderView, QFileDialog)
from PySide6.QtCore import Qt, QThread, Signal, QRectF, Property, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QIcon

from core.hardware import HardwareDetector
from core.analyzer import DiagnosticEngine
from core.report_generator import PDFReportGenerator
from core.sensors import HardwareSensors

class CircularGauge(QWidget):
    def __init__(self, color_hex="#22D3EE", size=80):
        super().__init__()
        self.setFixedSize(size, size)
        self._value = 0.0
        self._color = color_hex

    def get_value(self): return self._value
    def set_value(self, val):
        self._value = val
        self.update()

    value = Property(float, get_value, set_value)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        margin = 6
        rect = QRectF(margin, margin, self.width() - margin*2, self.height() - margin*2)
        
        pen_bg = QPen(QColor("#334155"), 8)
        pen_bg.setCapStyle(Qt.RoundCap)
        painter.setPen(pen_bg)
        painter.drawArc(rect, 0, 360 * 16)
        
        pen_val = QPen(QColor(self._color), 8)
        pen_val.setCapStyle(Qt.RoundCap)
        painter.setPen(pen_val)
        painter.drawArc(rect, 90 * 16, int(-self._value * 3.6 * 16))
        
        painter.setPen(QColor("#FAFAFA"))
        font = QFont("Segoe UI Variable Display", 11, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, f"{int(self._value)}%")


class DiagnosticWorker(QThread):
    progress_updated = Signal(int, str)
    scan_completed = Signal(dict, dict)

    def run(self):
        self.progress_updated.emit(20, "Inspection du processeur et de la mémoire...")
        os_info = HardwareDetector.get_os_info()
        cpu = HardwareDetector.get_cpu_info()
        time.sleep(0.2)
        ram = HardwareDetector.get_ram_info()
        time.sleep(0.2)
        self.progress_updated.emit(60, "Détection des cartes graphiques (GPU)...")
        gpus = HardwareDetector.get_gpu_info()
        time.sleep(0.2)
        disks = HardwareDetector.get_disks_info()
        physical_disks = HardwareDetector.get_physical_disks()
        time.sleep(0.2)

        hw = {
            "os": os_info, "cpu": cpu, "ram": ram, 
            "gpus": gpus, "disks": disks, "physical_disks": physical_disks
        }
        
        self.progress_updated.emit(90, "Génération du bilan de santé...")
        analysis = DiagnosticEngine.run_full_diagnostic(hw)
        time.sleep(0.1)
        
        self.progress_updated.emit(100, "Analyse terminée.")
        self.scan_completed.emit(hw, analysis)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PC Check")
        self.resize(1150, 720)
        self.setMinimumSize(950, 620)
        
        self.sensors_engine = HardwareSensors()
        self.live_timer = QTimer(self)
        self.live_timer.setInterval(1500) # Légèrement augmenté pour le parcours complet de l'arbre
        self.live_timer.timeout.connect(self.update_live_sensors)

        self.setStyleSheet("""
            QMainWindow { background-color: #0A0D14; }
            QLabel { color: #FAFAFA; font-family: 'Segoe UI Variable Display', 'Segoe UI', system-ui, sans-serif; }
            QFrame#sidebar { background-color: #11151C; border-right: 1px solid #334155; }
            QPushButton.nav-btn { background-color: transparent; color: #A1A1AA; font-size: 13px; font-weight: 500; text-align: left; padding: 10px 14px; border-radius: 6px; border: none; }
            QPushButton.nav-btn:hover { background-color: #1E293B; color: #FAFAFA; }
            QPushButton.nav-btn[active="true"] { background-color: #334155; color: #FAFAFA; font-weight: 600; }
            QFrame.panel { background-color: #151A23; border-radius: 8px; border: 1px solid #334155; }
            
            QPushButton#btn_scan { background-color: #F97316; color: #FFFFFF; font-weight: 600; font-size: 13px; padding: 8px 18px; border-radius: 6px; border: none; }
            QPushButton#btn_scan:hover { background-color: #EA580C; }
            QPushButton#btn_scan:disabled { background-color: #334155; color: #71717A; }
            QPushButton#btn_pdf { background-color: #334155; color: #FAFAFA; font-weight: 600; font-size: 13px; padding: 8px 18px; border-radius: 6px; border: 1px solid #3F3F46; }
            QPushButton#btn_pdf:hover { background-color: #3F3F46; }
            QPushButton#btn_pdf:disabled { background-color: #1E293B; color: #52525B; border: 1px solid #334155; }
            
            QPushButton.filter-btn { background-color: #1E293B; color: #A1A1AA; border: 1px solid #334155; border-radius: 4px; padding: 6px 12px; font-size: 12px; font-weight: 600; }
            QPushButton.filter-btn:hover { background-color: #334155; color: #FAFAFA; }
            QPushButton.filter-btn[active="true"] { background-color: #0EA5E9; color: #FAFAFA; border: 1px solid #0EA5E9; }

            QTreeWidget { background-color: #151A23; color: #FAFAFA; border: 1px solid #334155; border-radius: 6px; outline: 0; gridline-color: #334155; }
            QTreeWidget::item { padding: 4px; border-bottom: 1px solid #1c1c21; }
            QTreeWidget::item:selected { background-color: #334155; }
            QHeaderView::section { background-color: #1E293B; color: #A1A1AA; padding: 8px; border: none; border-right: 1px solid #334155; font-weight: 600; font-size: 12px; }
        """)

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(210)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 16, 12, 16)
        sidebar_layout.setSpacing(4)

        brand_lbl = QLabel("PC CHECK")
        brand_lbl.setStyleSheet("font-size: 15px; font-weight: 800; letter-spacing: 2px; color: #FAFAFA; padding: 6px 8px 16px 8px;")
        sidebar_layout.addWidget(brand_lbl)

        self.nav_buttons = {}
        self.nav_items = [("Vue d'ensemble", 0), ("Capteurs Détaillés", 1), ("Diagnostic", 2), ("Paramètres", 3)]

        for text, index in self.nav_items:
            btn = QPushButton(f"  {text}")
            btn.setProperty("class", "nav-btn")
            if index == 0: btn.setProperty("active", "true")
            btn.clicked.connect(lambda checked=False, idx=index: self.switch_page(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons[index] = btn
            
        sidebar_layout.addStretch()
        version_lbl = QLabel("v1.0.6 • LHM Tree View")
        version_lbl.setStyleSheet("color: #52525B; font-size: 11px; padding: 8px;")
        sidebar_layout.addWidget(version_lbl)
        layout.addWidget(sidebar)

        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(16)

        
        top_bar = QHBoxLayout()
        
        # --- AJOUT DU LOGO DANS L'UI ---
        self.logo_label = QLabel()
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png"))
        if os.path.exists(logo_path):
            from PySide6.QtGui import QPixmap
            pixmap = QPixmap(logo_path)
            # Redimensionner l'image pour qu'elle s'intègre bien (ex: 32x32 pixels)
            pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
        
        top_bar.addWidget(self.logo_label)
        # -------------------------------
        
        self.header_title = QLabel("Vue d'ensemble")

        self.header_title.setStyleSheet("font-size: 18px; font-weight: 700; color: #FAFAFA;")
        
        self.status_badge = QLabel("En attente d'analyse")
        self.status_badge.setStyleSheet("color: #A1A1AA; font-size: 12px; font-weight: 500; background: #1E293B; padding: 4px 10px; border-radius: 4px; border: 1px solid #334155;")

        self.btn_export = QPushButton("Exporter en PDF")
        self.btn_export.setObjectName("btn_pdf")
        self.btn_export.setEnabled(False)
        self.btn_export.clicked.connect(self.export_pdf)

        self.btn_scan = QPushButton("Lancer l'analyse")
        self.btn_scan.setObjectName("btn_scan")
        self.btn_scan.clicked.connect(self.start_scan)

        top_bar.addWidget(self.header_title)
        top_bar.addStretch()
        top_bar.addWidget(self.status_badge)
        top_bar.addWidget(self.btn_export)
        top_bar.addWidget(self.btn_scan)
        content_layout.addLayout(top_bar)

        self.loader_label = QLabel("")
        self.loader_label.setStyleSheet("color: #0EA5E9; font-size: 11px; font-weight: 600;")
        content_layout.addWidget(self.loader_label)

        self.stacked_widget = QStackedWidget()
        self.page_dashboard = self.create_dashboard_page()
        self.stacked_widget.addWidget(self.page_dashboard)

        self.page_components = self.create_components_page()
        self.stacked_widget.addWidget(self.page_components)

        self.page_diagnostic = self.create_diagnostic_page()
        self.stacked_widget.addWidget(self.page_diagnostic)

        self.page_settings = self.create_settings_page()
        self.stacked_widget.addWidget(self.page_settings)

        content_layout.addWidget(self.stacked_widget)
        layout.addWidget(content_frame)

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        self.header_title.setText(self.nav_items[index][0])
        for idx, btn in self.nav_buttons.items():
            btn.setProperty("active", "true" if idx == index else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        grid = QGridLayout()
        grid.setSpacing(12)

        self.p_cpu = self.create_data_panel("Processeur", "#0EA5E9")
        self.lbl_cpu_val = QLabel("En attente")
        self.lbl_cpu_val.setStyleSheet("font-size: 13px; font-weight: 600;")
        self.lbl_cpu_sub = QLabel("-")
        self.lbl_cpu_sub.setStyleSheet("color: #A1A1AA; font-size: 12px;")
        self.p_cpu.layout().addWidget(self.lbl_cpu_val)
        self.p_cpu.layout().addWidget(self.lbl_cpu_sub)
        self.p_cpu.layout().addStretch()
        grid.addWidget(self.p_cpu, 0, 0)

        self.p_ram = self.create_data_panel("Mémoire RAM", "#38BDF8")
        ram_h_layout = QHBoxLayout()
        ram_text_layout = QVBoxLayout()
        self.lbl_ram_val = QLabel("En attente")
        self.lbl_ram_val.setStyleSheet("font-size: 13px; font-weight: 600;")
        self.lbl_ram_sub = QLabel("-")
        self.lbl_ram_sub.setStyleSheet("color: #A1A1AA; font-size: 12px;")
        ram_text_layout.addWidget(self.lbl_ram_val)
        ram_text_layout.addWidget(self.lbl_ram_sub)
        ram_text_layout.addStretch()
        self.gauge_ram = CircularGauge(color_hex="#38BDF8", size=70)
        ram_h_layout.addLayout(ram_text_layout)
        ram_h_layout.addStretch()
        ram_h_layout.addWidget(self.gauge_ram)
        self.p_ram.layout().addLayout(ram_h_layout)
        grid.addWidget(self.p_ram, 0, 1)

        self.p_gpu = self.create_data_panel("Carte Graphique", "#F97316")
        self.gpu_container_layout = QVBoxLayout()
        self.gpu_container_layout.setContentsMargins(0, 0, 0, 0)
        self.gpu_container_layout.setSpacing(6)
        init_gpu_lbl = QLabel("En attente")
        init_gpu_lbl.setStyleSheet("color: #A1A1AA; font-size: 12px;")
        self.gpu_container_layout.addWidget(init_gpu_lbl)
        self.p_gpu.layout().addLayout(self.gpu_container_layout)
        self.p_gpu.layout().addStretch()
        grid.addWidget(self.p_gpu, 1, 0)

        self.p_disk = self.create_data_panel("Stockage Principal", "#F59E0B")
        disk_h_layout = QHBoxLayout()
        disk_text_layout = QVBoxLayout()
        self.lbl_disk_val = QLabel("En attente")
        self.lbl_disk_val.setStyleSheet("font-size: 13px; font-weight: 600;")
        self.lbl_disk_sub = QLabel("-")
        self.lbl_disk_sub.setStyleSheet("color: #A1A1AA; font-size: 12px;")
        disk_text_layout.addWidget(self.lbl_disk_val)
        disk_text_layout.addWidget(self.lbl_disk_sub)
        disk_text_layout.addStretch()
        self.gauge_disk = CircularGauge(color_hex="#F59E0B", size=70)
        disk_h_layout.addLayout(disk_text_layout)
        disk_h_layout.addStretch()
        disk_h_layout.addWidget(self.gauge_disk)
        self.p_disk.layout().addLayout(disk_h_layout)
        grid.addWidget(self.p_disk, 1, 1)

        layout.addLayout(grid)

        p_diag = self.create_data_panel("Bilan Rapide", "#FACC15")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.diag_container = QWidget()
        self.diag_layout = QVBoxLayout(self.diag_container)
        self.diag_layout.setContentsMargins(0, 0, 0, 0)
        self.diag_layout.setSpacing(8)
        
        init_msg = QLabel("Cliquez sur le bouton pour démarrer l'analyse.")
        init_msg.setStyleSheet("color: #52525B; font-size: 12px;")
        self.diag_layout.addWidget(init_msg)
        
        scroll.setWidget(self.diag_container)
        p_diag.layout().addWidget(scroll)
        layout.addWidget(p_diag, stretch=1)

        return page

    def create_components_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        subtitle = QLabel("Explorateur Matériel LHM - Affichage Hiérarchique Complet des Capteurs")
        subtitle.setStyleSheet("color: #A1A1AA; font-size: 12px;")
        layout.addWidget(subtitle)

        # Structure du nouvel arbre : Sensor | Value | Max
        self.comp_tree = QTreeWidget()
        self.comp_tree.setColumnCount(3)
        self.comp_tree.setHeaderLabels(["Sensor", "Value", "Max"])
        
        header = self.comp_tree.header()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        self.comp_tree.setColumnWidth(0, 400)
        self.comp_tree.setColumnWidth(1, 120)
        
        layout.addWidget(self.comp_tree)
        return page

    def create_diagnostic_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        filter_layout = QHBoxLayout()
        self.filter_buttons = {}
        for f_name in ["Tous", "CRITICAL", "WARNING", "INFO"]:
            btn = QPushButton(f_name)
            btn.setProperty("class", "filter-btn")
            if f_name == "Tous": btn.setProperty("active", "true")
            btn.clicked.connect(lambda checked=False, name=f_name: self.filter_diagnostic(name))
            filter_layout.addWidget(btn)
            self.filter_buttons[f_name] = btn
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.full_diag_container = QWidget()
        self.full_diag_layout = QVBoxLayout(self.full_diag_container)
        self.full_diag_layout.setContentsMargins(0, 0, 0, 0)
        self.full_diag_layout.setSpacing(8)
        
        init_lbl = QLabel("Aucune donnée. Lancez une analyse.")
        init_lbl.setStyleSheet("color: #52525B; font-size: 12px;")
        self.full_diag_layout.addWidget(init_lbl)
        
        scroll.setWidget(self.full_diag_container)
        layout.addWidget(scroll, stretch=1)

        return page

    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        panel_pdf = QFrame()
        panel_pdf.setProperty("class", "panel")
        pdf_layout = QVBoxLayout(panel_pdf)
        pdf_layout.setContentsMargins(16, 16, 16, 16)
        
        lbl_pdf_title = QLabel("Dossier d'enregistrement des rapports PDF")
        lbl_pdf_title.setStyleSheet("font-size: 13px; font-weight: 600; color: #FAFAFA;")
        
        self.lbl_pdf_path = QLabel(f"Actuel : Bureau ({os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop')})")
        self.lbl_pdf_path.setStyleSheet("color: #A1A1AA; font-size: 12px;")
        
        btn_change_dir = QPushButton("Modifier le dossier...")
        btn_change_dir.setStyleSheet("background-color: #334155; color: #FAFAFA; font-weight: 600; font-size: 12px; padding: 6px 12px; border-radius: 4px; border: 1px solid #3F3F46;")
        btn_change_dir.clicked.connect(self.change_export_dir)

        pdf_layout.addWidget(lbl_pdf_title)
        pdf_layout.addWidget(self.lbl_pdf_path)
        pdf_layout.addWidget(btn_change_dir, alignment=Qt.AlignLeft)
        layout.addWidget(panel_pdf)

        info_box = QFrame()
        info_box.setProperty("class", "panel")
        box_layout = QVBoxLayout(info_box)
        box_layout.setContentsMargins(16, 16, 16, 16)
        
        lbl_info = QLabel("<b>PC Check — Édition Professionnelle</b><br>Logiciel de diagnostic matériel haute performance 100% local.<br><br>• Version : 1.0.6 (LHM Tree View)<br>• Concepteur : Redouane MHEND")
        lbl_info.setStyleSheet("color: #D4D4D8; font-size: 13px; line-height: 1.5;")
        box_layout.addWidget(lbl_info)
        
        layout.addWidget(info_box)
        layout.addStretch()

        return page

    def change_export_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier d'exportation")
        if dir_path:
            self.custom_export_path = dir_path
            self.lbl_pdf_path.setText(f"Actuel : {dir_path}")

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
        self.btn_scan.setText("Analyse en cours...")
        self.status_badge.setText("Analyse...")
        self.status_badge.setStyleSheet("color: #0EA5E9; font-size: 12px; font-weight: 600; background: #1E293B; padding: 4px 10px; border-radius: 4px; border-bottom: 2px solid #0EA5E9;")
        
        self.lbl_cpu_val.setText("Analyse en cours...")
        self.lbl_ram_val.setText("Analyse en cours...")
        
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
        if not hasattr(self, '_animations'): self._animations = []
        self._animations.append(anim)

    def on_scan_finished(self, hw, analysis):
        try:
            self.loader_label.setText("")
            self.last_hw_data = hw
            self.last_analysis_data = analysis
            
            if hw.get('cpu'):
                self.lbl_cpu_val.setText(hw['cpu'].get('name', 'Inconnu'))
                self.lbl_cpu_sub.setText(f"{hw['cpu'].get('physical_cores', '-')} Cœurs Physiques\n{hw['cpu'].get('logical_cores', '-')} Cœurs Logiques")

            if hw.get('ram'):
                ram_brand = f"{hw['ram'].get('manufacturer', '')} {hw['ram'].get('part_number', '')}".strip()
                self.lbl_ram_val.setText(ram_brand if ram_brand else "Mémoire système")
                self.animate_gauge(self.gauge_ram, hw['ram'].get('percent_used', 0))
                ram_sub = f"{hw['ram'].get('total_gb', '-')} Go Total\n{hw['ram'].get('available_gb', '-')} Go libres"
                if hw['ram'].get('speed_mhz'): ram_sub += f"\n@ {hw['ram']['speed_mhz']} MHz"
                self.lbl_ram_sub.setText(ram_sub)

            while self.gpu_container_layout.count():
                child = self.gpu_container_layout.takeAt(0)
                if child.widget(): child.widget().deleteLater()

            if hw.get('gpus'):
                for gpu in hw['gpus']:
                    vram = f"{gpu.get('vram_gb', 'N/A')} Go" if gpu.get('vram_gb') else "N/A"
                    gpu_item_widget = QWidget()
                    gpu_item_layout = QVBoxLayout(gpu_item_widget)
                    gpu_item_layout.setContentsMargins(0, 2, 0, 2)
                    gpu_item_layout.setSpacing(1)
                    
                    name_lbl = QLabel(gpu.get('name', 'GPU Inconnu'))
                    name_lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #FAFAFA;")
                    sub_lbl = QLabel(f"VRAM : {vram} | Pilote : {gpu.get('driver_version', 'N/A')}")
                    sub_lbl.setStyleSheet("font-size: 11px; color: #A1A1AA;")
                    
                    gpu_item_layout.addWidget(name_lbl)
                    gpu_item_layout.addWidget(sub_lbl)
                    self.gpu_container_layout.addWidget(gpu_item_widget)
            else:
                no_gpu_lbl = QLabel("Aucun GPU détecté.")
                no_gpu_lbl.setStyleSheet("color: #A1A1AA; font-size: 12px;")
                self.gpu_container_layout.addWidget(no_gpu_lbl)

            if hw.get('physical_disks'):
                self.lbl_disk_val.setText(hw['physical_disks'][0].get('model', 'Disque principal'))
            
            if hw.get('disks'):
                d = hw['disks'][0]
                self.animate_gauge(self.gauge_disk, d.get('percent_used', 0))
                self.lbl_disk_sub.setText(f"Partition {d.get('mountpoint', 'C:')}\n{d.get('free_gb', '-')} Go libres sur {d.get('total_gb', '-')} Go")

            self.populate_components_tree_initial()
            self.populate_diagnostic_views(analysis)

            self.live_timer.start()

            status = analysis.get('overall_status', 'INCONNU')
            border_col = "#F97316" if status == "EXCELLENT" else "#F59E0B" if status == "À SURVEILLER" else "#EF4444"
            self.status_badge.setText(f"État : {status}")
            self.status_badge.setStyleSheet(f"color: #FAFAFA; font-size: 12px; font-weight: 600; background: #334155; padding: 4px 10px; border-radius: 4px; border-bottom: 2px solid {border_col};")

        except Exception as e:
            print(f"Erreur UI critique : {e}")
            self.status_badge.setText("Erreur d'affichage")
            self.status_badge.setStyleSheet("color: #FAFAFA; font-size: 12px; font-weight: 600; background: #7F1D1D; padding: 4px 10px; border-radius: 4px;")
            
        finally:
            self.btn_scan.setEnabled(True)
            self.btn_scan.setText("Actualiser l'analyse")
            self.btn_export.setEnabled(True)

    def get_color_for_category(self, cat_name):
        colors = {
            "Temperatures": "#EF4444",
            "Voltages": "#EAB308",
            "Loads": "#3B82F6",
            "Powers": "#DC2626",
            "Clocks": "#6366F1",
            "Data": "#8B5CF6",
            "Throughput": "#22C55E"
        }
        return QColor(colors.get(cat_name, "#A1A1AA"))

    def populate_components_tree_initial(self):
        """Construit l'arbre complet avec les catégories pour la première fois."""
        try:
            self.comp_tree.clear()
            metrics = self.sensors_engine.get_live_metrics()
            
            pc_root = QTreeWidgetItem(self.comp_tree, ["PC-LOCAL", "", ""])
            pc_root.setForeground(0, QColor("#FAFAFA"))

            for comp in metrics.get("components", []):
                # Ajout du composant (ex: AMD Ryzen 7 9700X)
                comp_item = QTreeWidgetItem(pc_root, [comp["name"], "", ""])
                comp_item.setForeground(0, QColor("#F8FAFC"))
                
                # On trie les catégories pour avoir un affichage propre
                for cat_name, sensors in sorted(comp["sensor_categories"].items()):
                    cat_item = QTreeWidgetItem(comp_item, [cat_name, "", ""])
                    cat_item.setForeground(0, self.get_color_for_category(cat_name))
                    
                    for sensor in sensors:
                        # Ajout du capteur avec sa valeur initiale (Max n'est pas encore géré, on met "-")
                        sensor_item = QTreeWidgetItem(cat_item, [sensor["name"], sensor["value"], sensor["value"]])
                        sensor_item.setForeground(0, QColor("#94A3B8"))
                        # Stocker la valeur max initiale
                        sensor_item.setData(2, Qt.UserRole, sensor["raw_value"])
            
            # Déplier le nœud principal
            self.comp_tree.expandItem(pc_root)
            
            # Déplier les composants
            for i in range(pc_root.childCount()):
                self.comp_tree.expandItem(pc_root.child(i))

        except Exception as e:
            print(f"Erreur remplissage arbre initial : {e}")

    def update_live_sensors(self):
        """Met à jour les valeurs de l'arbre existant sans le reconstruire."""
        try:
            metrics = self.sensors_engine.get_live_metrics()
            root = self.comp_tree.invisibleRootItem()
            
            if root.childCount() == 0:
                return
                
            pc_root = root.child(0)
            
            # Parcours de l'arbre existant pour mettre à jour les valeurs
            for c_idx in range(pc_root.childCount()):
                comp_item = pc_root.child(c_idx)
                comp_name = comp_item.text(0)
                
                # Chercher le composant correspondant dans les nouvelles métriques
                new_comp_data = next((c for c in metrics.get("components", []) if c["name"] == comp_name), None)
                if not new_comp_data: continue
                
                for cat_idx in range(comp_item.childCount()):
                    cat_item = comp_item.child(cat_idx)
                    cat_name = cat_item.text(0)
                    
                    new_sensors = new_comp_data["sensor_categories"].get(cat_name, [])
                    
                    for s_idx in range(cat_item.childCount()):
                        sensor_item = cat_item.child(s_idx)
                        sensor_name = sensor_item.text(0)
                        
                        # Chercher le capteur correspondant
                        new_s_data = next((s for s in new_sensors if s["name"] == sensor_name), None)
                        if new_s_data:
                            sensor_item.setText(1, new_s_data["value"])
                            
                            # Gestion de la valeur Max
                            current_max_raw = sensor_item.data(2, Qt.UserRole)
                            if current_max_raw is None or new_s_data["raw_value"] > current_max_raw:
                                sensor_item.setData(2, Qt.UserRole, new_s_data["raw_value"])
                                sensor_item.setText(2, new_s_data["value"])

        except Exception as e:
            pass # print(f"Erreur update arbre : {e}")

    def populate_diagnostic_views(self, analysis):
        while self.diag_layout.count():
            child = self.diag_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        for report in analysis['reports']:
            row = QFrame()
            row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            row.setStyleSheet("background: #0A0D14; border: 1px solid #334155; border-radius: 6px; padding: 6px;")
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

        self.all_reports_cache = analysis['reports']
        self.filter_diagnostic("Tous")

    def filter_diagnostic(self, filter_level):
        for name, btn in self.filter_buttons.items():
            btn.setProperty("active", "true" if name == filter_level else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        while self.full_diag_layout.count():
            child = self.full_diag_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        if not hasattr(self, 'all_reports_cache'): return

        filtered = [r for r in self.all_reports_cache if filter_level == "Tous" or r['level'] == filter_level]

        if not filtered:
            empty_lbl = QLabel("Aucun rapport ne correspond à ce filtre.")
            empty_lbl.setStyleSheet("color: #71717A; font-size: 12px;")
            self.full_diag_layout.addWidget(empty_lbl)
        else:
            for report in filtered:
                row = QFrame()
                row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                row.setStyleSheet("background: #151A23; border: 1px solid #334155; border-radius: 6px; padding: 8px;")
                r_box = QVBoxLayout(row)
                r_box.setContentsMargins(10, 8, 10, 8)

                lvl = report['level']
                color = "#EF4444" if lvl == "CRITICAL" else ("#F59E0B" if lvl == "WARNING" else "#10B981")

                t_row = QHBoxLayout()
                badge = QLabel(f"● {lvl}")
                badge.setStyleSheet(f"color: {color}; font-weight: 800; font-size: 11px;")
                t_lbl = QLabel(f"<b>{report['category']}</b> : {report['title']}")
                t_lbl.setStyleSheet("font-size: 13px; color: #FAFAFA;")
                t_row.addWidget(badge)
                t_row.addWidget(t_lbl)
                t_row.addStretch()
                r_box.addLayout(t_row)

                desc = QLabel(f"{report['description']}\n<b>Conseil :</b> {report['recommendation']}")
                desc.setStyleSheet("font-size: 12px; color: #A1A1AA; line-height: 1.4;")
                r_box.addWidget(desc)
                self.full_diag_layout.addWidget(row)
        
        self.full_diag_layout.addStretch()

    def export_pdf(self):
        if not hasattr(self, 'last_hw_data'): return
        try:
            export_dir = getattr(self, 'custom_export_path', os.path.join(os.environ['USERPROFILE'], 'Desktop'))
            path = PDFReportGenerator.generate_report(self.last_hw_data, self.last_analysis_data)
            
            if hasattr(self, 'custom_export_path') and self.custom_export_path != os.path.join(os.environ['USERPROFILE'], 'Desktop'):
                import shutil
                new_path = os.path.join(self.custom_export_path, os.path.basename(path))
                shutil.move(path, new_path)
                path = new_path
                
            QMessageBox.information(self, "Export réussi", f"Rapport PDF généré avec succès :\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de l'exportation.\n{e}")