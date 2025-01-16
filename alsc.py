#!/usr/bin/env python3
import sys
import os
import shutil
import psutil
import json
import logging
from datetime import datetime
from subprocess import Popen, PIPE, check_output
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QSettings, Qt, QTimer, QMetaObject, Q_ARG
from PyQt5.QtGui import *
from threading import Thread
from functools import partial

import os
from PyQt5.QtWidgets import (QDialog, QFileDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QMessageBox)
import subprocess
from pathlib import Path

# Stil tanımlamaları
DARK_STYLE = """
/* Ana Tema */
QMainWindow, QDialog, QWidget {
    background-color: #1a1a1a;
    color: #e0e0e0;
}

/* Butonlar */
QPushButton {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    color: #e0e0e0;
    padding: 5px 15px;
    border-radius: 3px;
}

QPushButton:hover {
    background-color: #3d3d3d;
}

QPushButton:pressed {
    background-color: #454545;
}

/* TreeWidget */
QTreeWidget {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    color: #e0e0e0;
}

QTreeWidget::item:selected {
    background-color: #404040;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #3d3d3d;
    border-radius: 3px;
    text-align: center;
    color: #e0e0e0;
}

QProgressBar::chunk {
    background-color: #2980b9;
}

/* Menu Bar */
QMenuBar {
    background-color: #2d2d2d;
    color: #e0e0e0;
}

QMenuBar::item:selected {
    background-color: #3d3d3d;
}

/* Status Bar */
QStatusBar {
    background-color: #2d2d2d;
    color: #e0e0e0;
}

/* Labels */
QLabel {
    color: #e0e0e0;
}
"""

# Stil tanımlamalarına ekleme
PROCESS_MANAGER_STYLE = """
QTableWidget {
    gridline-color: #3d3d3d;
}

QTableWidget QHeaderView::section {
    background-color: #2d2d2d;
    color: #e0e0e0;
    padding: 5px;
    border: 1px solid #3d3d3d;
}

QPushButton {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    border-radius: 3px;
    padding: 4px 8px;
    font-size: 12px;
    min-width: 80px;
    margin: 2px;
}

QPushButton:hover {
    background-color: #3d3d3d;
}

QPushButton:pressed {
    background-color: #454545;
}

QPushButton#stopButton {
    background-color: #c0392b;
}

QPushButton#stopButton:hover {
    background-color: #e74c3c;
}

QPushButton#restartButton {
    background-color: #27ae60;
}

QPushButton#restartButton:hover {
    background-color: #2ecc71;
}
"""

PROCESS_MANAGER_STYLE += """
QPushButton {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    padding: 5px 10px;
    border-radius: 3px;
}

QPushButton:hover {
    background-color: #3d3d3d;
}

QPushButton:pressed {
    background-color: #4d4d4d;
}
"""

# MessageBox stil tanımı
MSGBOX_STYLE = """
QMessageBox {
    background-color: #1a1a1a;
    color: #e0e0e0;
}
QMessageBox QLabel {
    color: #e0e0e0;
}
QMessageBox QPushButton {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    color: #e0e0e0;
    padding: 5px 15px;
    border-radius: 3px;
    min-width: 80px;
}
QMessageBox QPushButton:hover {
    background-color: #3d3d3d;
}
"""

# Stil tanımına ekle
MSGBOX_STYLE += """
QMessageBox {
    background-color: #1a1a1a;
}
QMessageBox QLabel {
    color: #e0e0e0;
    font-size: 12px;
}
QMessageBox QPushButton {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    color: #e0e0e0;
    padding: 5px 15px;
    border-radius: 3px;
    min-width: 80px;
}
QMessageBox QPushButton:hover {
    background-color: #3d3d3d;
}
"""

# Stil tanımlamaları eklemesi
STARTUP_MANAGER_STYLE = """
QDialog {
    background-color: #1a1a1a;
    color: #e0e0e0;
}

QLabel {
    color: #e0e0e0;
}

QLineEdit {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    padding: 5px;
    border-radius: 3px;
}

QTableWidget {
    gridline-color: #3d3d3d;
    background-color: #1a1a1a;
    color: #e0e0e0;
}

QTableWidget QHeaderView::section {
    background-color: #2d2d2d;
    color: #e0e0e0;
    padding: 5px;
    border: 1px solid #3d3d3d;
}

QPushButton {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    padding: 5px 10px;
    border-radius: 3px;
}

QPushButton:hover {
    background-color: #3d3d3d;
}

QPushButton:pressed {
    background-color: #4d4d4d;
}
"""

# Stil tanımlaması ekle
SYSTEM_INFO_STYLE = """
QDialog {
    background-color: #1a1a1a;
}

QGroupBox {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 5px;
    margin-top: 1ex;
    padding: 10px;
}

QGroupBox::title {
    color: #2196F3;
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    background-color: #1a1a1a;
}

QLabel {
    color: #e0e0e0;
    padding: 5px;
}

QLabel[type="header"] {
    color: #2196F3;
    font-size: 14px;
    font-weight: bold;
}

QLabel[type="value"] {
    color: #4CAF50;
    font-weight: bold;
}

QProgressBar {
    border: 1px solid #3d3d3d;
    border-radius: 3px;
    text-align: center;
    background-color: #2d2d2d;
}

QProgressBar::chunk {
    background-color: #2196F3;
    border-radius: 2px;
}
"""

# Disk Analizi için stil tanımı
DISK_ANALYZER_STYLE = """
QDialog {
    background-color: #1a1a1a;
}

QTreeWidget {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 5px;
    color: #e0e0e0;
    padding: 5px;
}

QTreeWidget::item {
    padding: 5px;
    border-bottom: 1px solid #3d3d3d;
}

QTreeWidget::item:selected {
    background-color: #2196F3;
}

QProgressBar {
    border: 1px solid #3d3d3d;
    border-radius: 3px;
    text-align: center;
    color: white;
    background-color: #2d2d2d;
    min-height: 20px;
}

QProgressBar::chunk {
    background-color: #2196F3;
    border-radius: 2px;
}

QPushButton {
    background-color: #2196F3;
    color: white;
    border: none;
    padding: 8px 15px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1976D2;
}

QPushButton:pressed {
    background-color: #0D47A1;
}

QLabel {
    color: #e0e0e0;
    font-size: 12px;
}
"""

# Log görüntüleyici için stil tanımı
LOG_VIEWER_STYLE = """
QDialog {
    background-color: #1a1a1a;
}

QTextEdit {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    border-radius: 3px;
    font-family: monospace;
    font-size: 12px;
    padding: 5px;
}

QLineEdit {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    border-radius: 3px;
    padding: 5px;
}

QPushButton {
    background-color: #2196F3;
    color: white;
    border: none;
    padding: 8px 15px;
    border-radius: 4px;
}

QPushButton:hover {
    background-color: #1976D2;
}

QLabel {
    color: #e0e0e0;
}

QComboBox {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    border-radius: 3px;
    padding: 5px;
}
"""

# Stil tanımına ekle
INFO_PANEL_STYLE = """
QGroupBox {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 8px;
    margin-top: 1ex;
    padding: 10px;
}

QGroupBox::title {
    color: #2196F3;
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    background-color: #1a1a1a;
    font-weight: bold;
}

QLabel {
    color: #e0e0e0;
    padding: 5px;
    font-size: 12px;
}

QLabel[type="header"] {
    color: #2196F3;
    font-size: 13px;
    font-weight: bold;
}

QLabel[type="value"] {
    color: #4CAF50;
    font-weight: bold;
    font-size: 13px;
}

QProgressBar {
    border: none;
    border-radius: 4px;
    text-align: center;
    background-color: #1a1a1a;
    height: 8px;
    font-size: 11px;
}

QProgressBar::chunk {
    border-radius: 4px;
}

QProgressBar::chunk[type="cpu"] {
    background-color: #2196F3;
}

QProgressBar::chunk[type="ram"] {
    background-color: #4CAF50;
}

QProgressBar::chunk[type="disk"] {
    background-color: #FFC107;
}
"""

# Stil tanımına ekle
CLEANUP_OPTIONS_STYLE = """
QTreeWidget {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 8px;
    padding: 5px;
    font-size: 12px;
}

QTreeWidget::item {
    padding: 8px;
    margin: 2px;
    border-radius: 4px;
}

QTreeWidget::item:hover {
    background-color: #3d3d3d;
}

QTreeWidget::item:selected {
    background-color: #2196F3;
    color: white;
}

QTreeWidget::branch {
    background: transparent;
}

QTreeWidget::branch:has-children:!has-siblings:closed,
QTreeWidget::branch:closed:has-children:has-siblings {
    border-image: none;
    image: url(right-arrow.png);
}

QTreeWidget::branch:open:has-children:!has-siblings,
QTreeWidget::branch:open:has-children:has-siblings {
    border-image: none;
    image: url(down-arrow.png);
}

QTreeWidget::indicator {
    width: 18px;
    height: 18px;
}

QTreeWidget::indicator:unchecked {
    border: 2px solid #3d3d3d;
    border-radius: 3px;
    background: #2d2d2d;
}

QTreeWidget::indicator:checked {
    border: 2px solid #2196F3;
    border-radius: 3px;
    background: #2196F3;
    image: url(checkmark.png);
}
"""

class AddStartupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Başlangıç Uygulaması Ekle")
        self.setFixedSize(400, 150)
        
        layout = QVBoxLayout()
        
        # Uygulama adı
        name_layout = QHBoxLayout()
        name_label = QLabel("Uygulama Adı:")
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        
        # Uygulama yolu
        path_layout = QHBoxLayout()
        path_label = QLabel("Uygulama Yolu:")
        self.path_input = QLineEdit()
        self.browse_button = QPushButton("Gözat")
        self.browse_button.clicked.connect(self.browse_file)
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_button)
        
        # Butonlar
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Kaydet")
        self.cancel_button = QPushButton("İptal")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(name_layout)
        layout.addLayout(path_layout)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Uygulama Seç", "", "Executable (*.exe)")
        if file_name:
            self.path_input.setText(file_name)
            if not self.name_input.text():
                self.name_input.setText(os.path.basename(file_name))

class StartupManager:
    def __init__(self):
        self.autostart_dir = os.path.expanduser('~/.config/autostart')
        os.makedirs(self.autostart_dir, exist_ok=True)

    def get_startup_items(self):
        items = []
        for file in os.listdir(self.autostart_dir):
            if file.endswith('.desktop'):
                file_path = os.path.join(self.autostart_dir, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                    name = file.replace('.desktop', '')
                    exec_path = ''
                    enabled = True
                    for line in content.split('\n'):
                        if line.startswith('Exec='):
                            exec_path = line.replace('Exec=', '')
                        elif line.startswith('Hidden=true'):
                            enabled = False
                    items.append({"name": name, "path": exec_path, "enabled": enabled})
        return items

    def add_startup_item(self, name, path):
        try:
            desktop_content = f"""[Desktop Entry]
Type=Application
Name={name}
Exec={path}
Hidden=false
Terminal=false
X-GNOME-Autostart-enabled=true"""
            
            file_path = os.path.join(self.autostart_dir, f"{name}.desktop")
            with open(file_path, 'w') as f:
                f.write(desktop_content)
            os.chmod(file_path, 0o755)
            return True
        except Exception as e:
            logging.error(f"Başlangıç uygulaması eklenirken hata: {str(e)}")
            return False

    def toggle_startup_item(self, name, enable):
        try:
            file_path = os.path.join(self.autostart_dir, f"{name}.desktop")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                
                with open(file_path, 'w') as f:
                    for line in lines:
                        if line.startswith('Hidden='):
                            f.write(f'Hidden={"false" if enable else "true"}\n')
                        else:
                            f.write(line)
                return True
        except Exception as e:
            logging.error(f"Başlangıç uygulaması durumu değiştirilirken hata: {str(e)}")
            return False

    def remove_startup_item(self, name):
        try:
            file_path = os.path.join(self.autostart_dir, f"{name}.desktop")
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            logging.error(f"Başlangıç uygulaması kaldırılırken hata: {str(e)}")
            return False

class SystemCleaner(QMainWindow):
    # Sinyalleri tanımla
    progress_updated = pyqtSignal(int, int)
    process_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        
        # Kategorileri tanımla
        self.categories = {
            "Sistem": [
                "Önbellek",
                "Geçici Dosyalar", 
                "Paket Önbelleği",
                "Eski Kernel Dosyaları",
                "Günlük Dosyaları",
                "Çöp Kutusu" # Yeni eklendi
            ],
            "Tarayıcılar": [
                "Chrome Önbelleği",
                "Firefox Önbelleği", 
                "Opera Önbelleği",
                "İndirilenler Geçmişi"
            ],
            "Uygulamalar": [
                "Uygulama Önbelleği",
                "Thumbnail Önbelleği",
                "Apt Önbelleği",
                "Snap Önbelleği",
                "Flatpak Önbelleği"
            ]
        }
        
        # Icon yollarını al
        self.ICON_PATH = self.get_icon_path()
        self.LOGO_PATH = self.get_logo_path()
        
        # Pencere ayarları
        self.setWindowTitle("ALSC - Advanced Linux System Cleaner")
        self.setMinimumSize(1000, 700)
        
        # İkon ayarları
        if self.ICON_PATH:
            icon = QIcon(self.ICON_PATH)
            self.setWindowIcon(icon)
            QApplication.setWindowIcon(icon)
        
        self.settings = QSettings('ALSC', 'Preferences')
        self.total_space_cleaned = 0
        self.cleanup_running = False
        self.analyze_running = False
        self.setup_ui()
        self.create_menu_bar()
        self.setup_status_bar()
        self.setup_logging()
        self.setStyleSheet(DARK_STYLE)
        self.progress_updated.connect(self.update_progress)
        self.process_finished.connect(self.on_process_finished)
        self.error_occurred.connect(self.show_error_message)
        self.load_settings()
        
        # Status bar oluştur
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def get_logo_path(self):
        """Logo dosyasının yolunu döndürür."""
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, "alsclo.png")
        elif os.path.exists("/usr/share/icons/hicolor/48x48/apps/alsclo.png"):
            return "/usr/share/icons/hicolor/48x48/apps/alsclo.png"
        elif os.path.exists("alsclo.png"):
            return "alsclo.png"
        return None

    def get_icon_path(self):
        """Simge dosyasının yolunu döndürür."""
        icon_paths = [
            os.path.join(os.path.dirname(__file__), "alsclo.png"),
            "/usr/share/icons/hicolor/48x48/apps/alsclo.png",
            os.path.join(os.getcwd(), "alsclo.png")
        ]
        
        for path in icon_paths:
            if os.path.exists(path):
                return path
        return None

    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # Dosya Menüsü
        file_menu = menubar.addMenu('Dosya')
        
        save_action = QAction('Ayarları Kaydet', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_settings)
        
        load_action = QAction('Ayarları Yükle', self)
        load_action.setShortcut('Ctrl+L')
        load_action.triggered.connect(self.load_settings)
        
        exit_action = QAction('Çıkış', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        
        file_menu.addAction(save_action)
        file_menu.addAction(load_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # Araçlar Menüsü
        tools_menu = menubar.addMenu('Araçlar')
        
        system_info = QAction('Sistem Bilgileri', self)
        system_info.triggered.connect(self.show_system_info)
        
        disk_analyzer = QAction('Disk Analizi', self)
        disk_analyzer.triggered.connect(self.show_disk_analyzer)
        
        startup_manager = QAction('Başlangıç Yöneticisi', self)
        startup_manager.triggered.connect(self.show_startup_manager)
        
        process_manager = QAction('Süreç Yöneticisi', self)
        process_manager.triggered.connect(self.show_process_manager)
        
        log_viewer = QAction('Log Görüntüleyici', self)
        log_viewer.triggered.connect(self.show_log_viewer)
        
        tools_menu.addAction(system_info)
        tools_menu.addAction(disk_analyzer)
        tools_menu.addAction(startup_manager)
        tools_menu.addAction(process_manager)
        tools_menu.addAction(log_viewer)

        # RAM Temizle butonu ekle
        clear_ram_action = QAction("RAM Temizle", self)
        clear_ram_action.triggered.connect(self.clear_memory)
        self.menuBar().addAction(clear_ram_action)
        
        # Hakkında Menüsü
        about_menu = menubar.addMenu('Yardım')
        about_action = QAction('Hakkında', self)
        about_action.triggered.connect(self.show_about)
        about_menu.addAction(about_action)

    def show_about(self):
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle("Yardım")
        about_dialog.setFixedSize(600, 600)
        
        layout = QVBoxLayout()
        
        # Logo ekle
        if self.LOGO_PATH:
            logo_label = QLabel()
            pixmap = QPixmap(self.LOGO_PATH)
            scaled_pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        
        # Başlık
        title_label = QLabel("ALSC - Advanced Linux System Cleaner")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2196F3;")
        title_label.setAlignment(Qt.AlignCenter)
        
        info_text = """
        <p>Bu program, Linux sistemlerde bakım ve temizlik işlemlerini kolaylaştırmak için geliştirilmiştir.</p>
        <br>
                <p><b>Özellikler:</b></p>
        <ul>
            <li>Sistem temizliği</li>
            <li>RAM optimizasyonu</li>
            <li>Süreç yönetimi</li>
            <li>Disk analizi</li>
            <li>Log görüntüleyici</li>
            <li>Başlangıç yöneticisi</li>
        </ul>
        <p>Geliştirici: ALG Yazılım Inc.©</p>
        <p>www.algyazilim.com | info@algyazilim.com</p>
        <p>Fatih ÖNDER (CekToR) | fatih@algyazilim.com</p>
        <p>GitHub: https://github.com/cektor</p>
        <p>Sürüm: 1.0</p>
        <p>ALG Yazılım Pardus'a Göç'ü Destekler.</p>
        <p>Telif Hakkı © 2024 GNU</p>


        <br>
        
        """
        
        info_label = QLabel(info_text)
        info_label.setOpenExternalLinks(True)
        info_label.setWordWrap(True)
        
        close_button = QPushButton("Kapat")
        close_button.clicked.connect(about_dialog.close)
        close_button.setFixedWidth(100)
        
        layout.addWidget(title_label)
        layout.addWidget(info_label)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)
        
        about_dialog.setLayout(layout)
        
        if self.ICON_PATH:
            about_dialog.setWindowIcon(QIcon(self.ICON_PATH))
        
        about_dialog.exec_()

    def show_system_info(self):
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Sistem Bilgileri")
            dialog.setMinimumSize(600, 500)
            dialog.setStyleSheet(SYSTEM_INFO_STYLE)

            layout = QGridLayout()
            
            # CPU Bilgileri
            cpu_group = QGroupBox("CPU Bilgileri")
            cpu_layout = QGridLayout()
            
            # CPU model bilgisi
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    cpu_data = f.readlines()
                cpu_model = ""
                for line in cpu_data:
                    if 'model name' in line:
                        cpu_model = line.split(':')[1].strip()
                        break
            except:
                cpu_model = "Bilinmiyor"
            
            cpu_layout.addWidget(QLabel(f"Model: {cpu_model}"), 0, 0)
            
            # CPU Kullanımı
            try:
                cpu_usage = psutil.cpu_percent(interval=1)
                cpu_bar = QProgressBar()
                cpu_bar.setValue(int(round(cpu_usage)))
                cpu_layout.addWidget(QLabel("Kullanım:"), 1, 0)
                cpu_layout.addWidget(cpu_bar, 1, 1)
                cpu_layout.addWidget(QLabel(f"{cpu_usage:.1f}%"), 1, 2)
            except:
                cpu_layout.addWidget(QLabel("CPU kullanımı alınamadı"), 1, 0)
            
            # CPU Frekansı
            try:
                freq = psutil.cpu_freq()
                if freq:
                    cpu_layout.addWidget(QLabel(f"Frekans: {freq.current:.1f} MHz"), 2, 0)
            except:
                cpu_layout.addWidget(QLabel("Frekans bilgisi alınamadı"), 2, 0)
            
            cpu_group.setLayout(cpu_layout)
            layout.addWidget(cpu_group, 0, 0)
            
            # RAM Bilgileri
            ram_group = QGroupBox("RAM Bilgileri")
            ram_layout = QGridLayout()
            
            try:
                mem = psutil.virtual_memory()
                total_ram = mem.total / (1024**3)
                used_ram = mem.used / (1024**3)
                free_ram = mem.free / (1024**3)
                
                ram_bar = QProgressBar()
                ram_bar.setValue(int(round(mem.percent)))
                
                ram_layout.addWidget(QLabel(f"Toplam: {total_ram:.1f} GB"), 0, 0)
                ram_layout.addWidget(QLabel("Kullanım:"), 1, 0)
                ram_layout.addWidget(ram_bar, 1, 1)
                ram_layout.addWidget(QLabel(f"{mem.percent:.1f}%"), 1, 2)
                ram_layout.addWidget(QLabel(f"Boş: {free_ram:.1f} GB"), 2, 0)
            except:
                ram_layout.addWidget(QLabel("RAM bilgileri alınamadı"), 0, 0)
            
            ram_group.setLayout(ram_layout)
            layout.addWidget(ram_group, 0, 1)
            
            # Disk Bilgileri
            disk_group = QGroupBox("Disk Bilgileri")
            disk_layout = QGridLayout()
            
            try:
                disk = psutil.disk_usage('/')
                total_disk = disk.total / (1024**3)
                used_disk = disk.used / (1024**3)
                free_disk = disk.free / (1024**3)
                
                disk_bar = QProgressBar()
                disk_bar.setValue(int(round(disk.percent)))
                
                disk_layout.addWidget(QLabel(f"Toplam: {total_disk:.1f} GB"), 0, 0)
                disk_layout.addWidget(QLabel("Kullanım:"), 1, 0)
                disk_layout.addWidget(disk_bar, 1, 1)
                disk_layout.addWidget(QLabel(f"{disk.percent:.1f}%"), 1, 2)
                disk_layout.addWidget(QLabel(f"Boş: {free_disk:.1f} GB"), 2, 0)
            except:
                disk_layout.addWidget(QLabel("Disk bilgileri alınamadı"), 0, 0)
            
            disk_group.setLayout(disk_layout)
            layout.addWidget(disk_group, 1, 0)
            
            # Sistem Bilgileri
            system_group = QGroupBox("Sistem Bilgileri")
            system_layout = QGridLayout()
            
            try:
                os_info = os.uname()
                system_layout.addWidget(QLabel(f"İşletim Sistemi: {os_info.sysname} {os_info.release}"), 0, 0)
                system_layout.addWidget(QLabel(f"Bilgisayar Adı: {os_info.nodename}"), 1, 0)
                system_layout.addWidget(QLabel(f"Versiyon: {os_info.version}"), 2, 0)
            except:
                system_layout.addWidget(QLabel("Sistem bilgileri alınamadı"), 0, 0)
            
            system_group.setLayout(system_layout)
            layout.addWidget(system_group, 1, 1)
            
            # Yenile butonu
            refresh_btn = QPushButton("Yenile")
            refresh_btn.clicked.connect(lambda: self.refresh_system_info(dialog))
            layout.addWidget(refresh_btn, 2, 0, 1, 2)
            
            dialog.setLayout(layout)
            dialog.exec_()
            
        except Exception as e:
            logging.error(f"Sistem bilgileri gösterilirken hata: {str(e)}")
            self.show_error("Hata", "Sistem bilgileri gösterilirken bir hata oluştu.")

    def refresh_system_info(self, dialog):
        """Sistem bilgilerini yeniler"""
        dialog.close()
        self.show_system_info()

    def show_disk_analyzer(self):
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Disk Analizi")
            dialog.setMinimumSize(800, 600)
            dialog.setStyleSheet(DISK_ANALYZER_STYLE)
            
            layout = QVBoxLayout()

            # Başlık
            title = QLabel("💾 Disk Kullanım Analizi")
            title.setStyleSheet("font-size: 18px; color: #2196F3; font-weight: bold; padding: 10px;")
            title.setAlignment(Qt.AlignCenter)
            layout.addWidget(title)

            # Genel disk kullanımı
            disk_info = psutil.disk_usage('/')
            total = disk_info.total / (1024**3)
            used = disk_info.used / (1024**3)
            free = disk_info.free / (1024**3)

            info_widget = QWidget()
            info_layout = QHBoxLayout()
            
            # Disk kullanım çubuğu
            usage_bar = QProgressBar()
            usage_bar.setMaximum(100)
            usage_bar.setValue(int(disk_info.percent))
            usage_bar.setFormat(f"Kullanılan: {used:.1f} GB / Toplam: {total:.1f} GB")
            info_layout.addWidget(usage_bar)
            
            info_widget.setLayout(info_layout)
            layout.addWidget(info_widget)

            # Progress bar
            progress = QProgressBar()
            progress.setFormat("%p%")
            layout.addWidget(progress)

            # Treeview
            tree = QTreeWidget()
            tree.setHeaderLabels(["Dizin", "Boyut", "Kullanım Oranı"])
            tree.setAlternatingRowColors(True)
            tree.setColumnWidth(0, 400)
            layout.addWidget(tree)

            def analyze_directory(path, parent_item=None):
                try:
                    total = 0
                    items = []
                    
                    for entry in os.scandir(path):
                        try:
                            if entry.is_file():
                                size = entry.stat().st_size
                                items.append((entry.name, size, True))
                                total += size
                            elif entry.is_dir():
                                dir_size = 0
                                for root, dirs, files in os.walk(entry.path):
                                    for f in files:
                                        try:
                                            dir_size += os.path.getsize(os.path.join(root, f))
                                        except:
                                            continue
                                items.append((entry.name, dir_size, False))
                                total += dir_size
                        except PermissionError:
                            continue

                    items.sort(key=lambda x: x[1], reverse=True)
                    
                    for name, size, is_file in items:
                        size_str = self.format_size(size)
                        percent = (size / total * 100) if total > 0 else 0
                        
                        item = QTreeWidgetItem([
                            name,
                            size_str,
                            f"{percent:.1f}%"
                        ])
                        
                        # Dosya/Klasör ikonları ve renkleri
                        if is_file:
                            item.setIcon(0, self.style().standardIcon(QStyle.SP_FileIcon))
                        else:
                            item.setIcon(0, self.style().standardIcon(QStyle.SP_DirIcon))
                            item.setForeground(0, QColor("#2196F3"))
                        
                        if parent_item:
                            parent_item.addChild(item)
                        else:
                            tree.addTopLevelItem(item)

                    return total
                except PermissionError:
                    return 0

            def start_analysis():
                try:
                    tree.clear()
                    progress.setMaximum(0)
                    analyze_directory(os.path.expanduser("~"))
                    progress.setMaximum(100)
                    progress.setValue(100)
                    self.show_info("Analiz Tamamlandı", "Disk analizi başarıyla tamamlandı!")
                except Exception as e:
                    self.show_error("Hata", f"Analiz sırasında hata: {str(e)}")

            # Butonlar
            button_widget = QWidget()
            button_layout = QHBoxLayout(button_widget)
            
            analyze_btn = QPushButton("🔍 Analizi Başlat")
            analyze_btn.clicked.connect(start_analysis)
            button_layout.addWidget(analyze_btn)
            
            refresh_btn = QPushButton("🔄 Yenile")
            refresh_btn.clicked.connect(start_analysis)
            button_layout.addWidget(refresh_btn)
            
            button_widget.setLayout(button_layout)
            layout.addWidget(button_widget)

            dialog.setLayout(layout)
            dialog.exec_()

        except Exception as e:
            self.show_error("Disk Analizi Hatası", str(e))

    def show_startup_manager(self):
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Başlangıç Yöneticisi")
            dialog.setMinimumSize(800, 500)
            dialog.setStyleSheet(STARTUP_MANAGER_STYLE)
            
            layout = QVBoxLayout()
            
            # Başlık
            title = QLabel("🚀 Başlangıç Uygulamaları Yöneticisi")
            title.setStyleSheet("font-size: 18px; color: #2196F3; font-weight: bold; padding: 10px;")
            title.setAlignment(Qt.AlignCenter)
            layout.addWidget(title)

            # Tablo güncelleme
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Program", "Durum", "Yol", "İşlemler"])
            
            # Sütun genişliklerini ayarla 
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Fixed)  # Program adı
            header.setSectionResizeMode(1, QHeaderView.Fixed)  # Durum
            header.setSectionResizeMode(2, QHeaderView.Stretch) # Yol
            header.setSectionResizeMode(3, QHeaderView.Fixed)  # İşlemler

            table.setColumnWidth(0, 150)  # Program
            table.setColumnWidth(1, 80)   # Durum  
            table.setColumnWidth(3, 220)  # İşlemler
            
            layout.addWidget(table)

            # Butonlar için widget
            button_widget = QWidget()
            button_layout = QHBoxLayout()
            
            add_btn = QPushButton("➕ Uygulama Ekle")
            add_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
            
            refresh_btn = QPushButton("🔄 Yenile")
            refresh_btn.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
            
            button_layout.addWidget(add_btn)
            button_layout.addWidget(refresh_btn)
            button_widget.setLayout(button_layout)
            layout.addWidget(button_widget)

            def load_startup_items():
                table.setRowCount(0)
                startup_dir = os.path.expanduser("~/.config/autostart")
                
                if os.path.exists(startup_dir):
                    for file in os.listdir(startup_dir):
                        if file.endswith('.desktop'):
                            row = table.rowCount()
                            table.insertRow(row)
                            
                            name = file.replace('.desktop', '')
                            path = os.path.join(startup_dir, file)
                            
                            # Program adı
                            table.setItem(row, 0, QTableWidgetItem(name))
                            
                            # Durum
                            with open(path, 'r') as f:
                                content = f.read()
                                enabled = "Hidden=true" not in content
                            status = QTableWidgetItem("Aktif" if enabled else "Pasif")
                            status.setForeground(QColor("#4CAF50" if enabled else "#F44336"))
                            table.setItem(row, 1, status)
                            
                            # Yol
                            table.setItem(row, 2, QTableWidgetItem(path))
                            
                            # İşlem butonları güncelleme
                            btn_widget = QWidget()
                            btn_layout = QHBoxLayout(btn_widget)
                            btn_layout.setContentsMargins(4, 2, 4, 2)
                            
                            toggle_btn = QPushButton("Aç/Kpt") 
                            toggle_btn.setFixedWidth(70)
                            toggle_btn.clicked.connect(lambda checked, n=name: toggle_startup_item(n))
                            
                            remove_btn = QPushButton("Sil")
                            remove_btn.setFixedWidth(50)
                            remove_btn.clicked.connect(lambda checked, n=name: remove_startup_item(n))
                            
                            for btn in [toggle_btn, remove_btn]:
                                btn_layout.addWidget(btn)
                            
                            table.setCellWidget(row, 3, btn_widget)

            def add_startup_item():
                dialog = AddStartupDialog(self)
                if dialog.exec_() == QDialog.Accepted:
                    name = dialog.name_input.text()
                    path = dialog.path_input.text()
                    if name and path:
                        success = self.startup_manager.add_startup_item(name, path)
                        if success:
                            load_startup_items()
                            self.show_info("Başarılı", "Uygulama başlangıca eklendi.")
                        else:
                            self.show_error("Hata", "Uygulama eklenirken hata oluştu.")

            def toggle_startup_item(name):
                try:
                    file_path = os.path.join(os.path.expanduser("~/.config/autostart"), f"{name}.desktop")
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            content = f.readlines()
                            enabled = True
                            for line in content:
                                if line.startswith('Hidden=true'):
                                    enabled = False
                                    break
                        
                        with open(file_path, 'w') as f:
                            for line in content:
                                if line.startswith('Hidden='):
                                    f.write(f'Hidden={"false" if enabled else "true"}\n')
                                else:
                                    f.write(line)
                        load_startup_items()
                except Exception as e:
                    self.show_error("Hata", f"Durum değiştirme hatası: {str(e)}")

            def remove_startup_item(name):
                try:
                    file_path = os.path.join(os.path.expanduser("~/.config/autostart"), f"{name}.desktop")
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        load_startup_items()
                        self.show_info("Başarılı", "Uygulama başlangıçtan kaldırıldı.")
                except Exception as e:
                    self.show_error("Hata", f"Kaldırma hatası: {str(e)}")

            # Sinyal bağlantıları
            add_btn.clicked.connect(add_startup_item)
            refresh_btn.clicked.connect(load_startup_items)

            # İlk yükleme
            load_startup_items()
            
            dialog.setLayout(layout)
            dialog.exec_()
            
        except Exception as e:
            self.show_error("Başlangıç Yöneticisi Hatası", str(e))

    def show_process_manager(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Süreç Yöneticisi")
        dialog.setMinimumSize(800, 600)
        dialog.setStyleSheet(PROCESS_MANAGER_STYLE)
        layout = QVBoxLayout()

        # Arama kutusu
        search_box = QLineEdit()
        search_box.setPlaceholderText("Süreç ara...")
        layout.addWidget(search_box)

        # Süreç tablosu
        process_table = QTableWidget()
        process_table.setColumnCount(6)
        process_table.setHorizontalHeaderLabels(["PID", "İsim", "CPU %", "Bellek %", "Durum", "İşlemler"])
        layout.addWidget(process_table)

        def update_processes():
            process_table.setRowCount(0)
            search_text = search_box.text().lower()
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    if search_text and search_text not in proc.info['name'].lower():
                        continue
                        
                    row = process_table.rowCount()
                    process_table.insertRow(row)
                    
                    # Süreç bilgileri
                    for col, value in enumerate([
                        str(proc.info['pid']),
                        proc.info['name'],
                        f"{proc.info['cpu_percent']:.1f}%",
                        f"{proc.info['memory_percent']:.1f}%",
                        proc.info['status']
                    ]):
                        item = QTableWidgetItem(value)
                        item.setTextAlignment(Qt.AlignCenter)
                        process_table.setItem(row, col, item)
                    
                    # İşlem butonları
                    btn_widget = QWidget()
                    btn_layout = QHBoxLayout(btn_widget)
                    btn_layout.setContentsMargins(4, 2, 4, 2)
                    btn_layout.setSpacing(4)
                    
                    stop_btn = QPushButton("Durdur")
                    stop_btn.setObjectName("stopButton")
                    stop_btn.setFixedWidth(90)
                    stop_btn.clicked.connect(lambda: kill_process(proc.info['pid']))
                    
                    restart_btn = QPushButton("Y.Başlat")
                    restart_btn.setObjectName("restartButton")
                    restart_btn.setFixedWidth(90)
                    restart_btn.clicked.connect(lambda: restart_process(proc.info['pid']))
                    
                    for btn in [stop_btn, restart_btn]:
                        btn_layout.addWidget(btn)
                    
                    process_table.setCellWidget(row, 5, btn_widget)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        # Tablo başlıklarını ayarla
        header = process_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        
        process_table.setColumnWidth(0, 80)   # PID
        process_table.setColumnWidth(2, 100)  # CPU
        process_table.setColumnWidth(3, 100)  # Bellek
        process_table.setColumnWidth(4, 100)  # Durum
        process_table.setColumnWidth(5, 200)  # İşlemler

        def kill_process(pid):
            try:
                os.kill(pid, 9)
                update_processes()
            except Exception as e:
                self.show_error("Süreç Durdurma Hatası", str(e))

        def restart_process(pid):
            try:
                proc = psutil.Process(pid)
                cmd = proc.cmdline()
                proc.kill()
                if cmd:
                    Popen(cmd)
                update_processes()
            except Exception as e:
                self.show_error("Süreç Yeniden Başlatma Hatası", str(e))

        # Yenile butonu
        refresh_btn = QPushButton("Yenile")
        refresh_btn.clicked.connect(update_processes)
        layout.addWidget(refresh_btn)

        # Arama kutusuna yazıldıkça filtreleme
        search_box.textChanged.connect(update_processes)

        update_processes()
        dialog.setLayout(layout)
        dialog.exec_()

    def show_log_viewer(self):
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Log Görüntüleyici")
            dialog.setMinimumSize(800, 600)
            dialog.setStyleSheet(LOG_VIEWER_STYLE)
            
            layout = QVBoxLayout()
            
            # Başlık
            title = QLabel("📋 Sistem Logları")
            title.setStyleSheet("font-size: 18px; color: #2196F3; font-weight: bold; padding: 10px;")
            title.setAlignment(Qt.AlignCenter)
            layout.addWidget(title)
            
            # Filtre araçları
            filter_layout = QHBoxLayout()
            
            search_input = QLineEdit()
            search_input.setPlaceholderText("Log içinde ara...")
            
            level_combo = QComboBox()
            level_combo.addItems(["Tümü", "INFO", "WARNING", "ERROR"])
            
            filter_layout.addWidget(search_input)
            filter_layout.addWidget(level_combo)
            layout.addLayout(filter_layout)
            
            # Log görüntüleyici
            self.log_text = QTextEdit()
            self.log_text.setReadOnly(True)
            layout.addWidget(self.log_text)
            
            # Butonlar
            button_layout = QHBoxLayout()
            
            refresh_btn = QPushButton("🔄 Yenile")
            clear_btn = QPushButton("🗑️ Temizle")
            export_btn = QPushButton("💾 Dışa Aktar")
            
            for btn in [refresh_btn, clear_btn, export_btn]:
                button_layout.addWidget(btn)
            
            layout.addLayout(button_layout)
            
            def load_logs():
                try:
                    log_file = os.path.expanduser("~/.alsc/logs/alsc.log")
                    if os.path.exists(log_file):
                        with open(log_file, 'r') as f:
                            content = f.read()
                            self.log_text.setPlainText(content)
                    else:
                        self.log_text.setPlainText("Log dosyası bulunamadı.")
                except Exception as e:
                    self.log_text.setPlainText(f"Log okuma hatası: {str(e)}")

            def filter_logs():
                search_text = search_input.text().lower()
                level_filter = level_combo.currentText()
                
                try:
                    log_file = os.path.expanduser("~/.alsc/logs/alsc.log")
                    if os.path.exists(log_file):
                        with open(log_file, 'r') as f:
                            lines = f.readlines()
                            
                        filtered_lines = []
                        for line in lines:
                            if level_filter != "Tümü" and level_filter not in line:
                                continue
                            if search_text and search_text not in line.lower():
                                continue
                            filtered_lines.append(line)
                        
                        self.log_text.setPlainText("".join(filtered_lines))
                except Exception as e:
                    self.log_text.setPlainText(f"Filtreleme hatası: {str(e)}")

            def clear_logs():
                try:
                    log_file = os.path.expanduser("~/.alsc/logs/alsc.log")
                    if os.path.exists(log_file):
                        with open(log_file, 'w') as f:
                            f.write("")
                        self.log_text.clear()
                        self.show_info("Başarılı", "Loglar temizlendi.")
                except Exception as e:
                    self.show_error("Hata", f"Log temizleme hatası: {str(e)}")

            def export_logs():
                try:
                    filename, _ = QFileDialog.getSaveFileName(
                        dialog,
                        "Logları Kaydet",
                        os.path.expanduser("~/alsc_logs.txt"),
                        "Text Files (*.txt)"
                    )
                    if filename:
                        with open(filename, 'w') as f:
                            f.write(self.log_text.toPlainText())
                        self.show_info("Başarılı", "Loglar dışa aktarıldı.")
                except Exception as e:
                    self.show_error("Hata", f"Dışa aktarma hatası: {str(e)}")

            # Sinyal bağlantıları
            refresh_btn.clicked.connect(load_logs)
            clear_btn.clicked.connect(clear_logs)
            export_btn.clicked.connect(export_logs)
            search_input.textChanged.connect(filter_logs)
            level_combo.currentTextChanged.connect(filter_logs)
            
            # Otomatik güncelleme için timer
            timer = QTimer()
            timer.timeout.connect(load_logs)
            timer.start(5000)  # Her 5 saniyede bir güncelle
            
            dialog.setLayout(layout)
            
            # İlk yükleme
            load_logs()
            
            dialog.exec_()
            
        except Exception as e:
            self.show_error("Log Görüntüleyici Hatası", str(e))

    def setup_status_bar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Sistem bilgileri
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        self.cpu_label = QLabel(f"CPU: {cpu_usage}%")
        self.mem_label = QLabel(f"RAM: {memory.percent}%")
        self.disk_label = QLabel(f"Disk: {disk.percent}%")
        
        self.statusBar.addPermanentWidget(self.cpu_label)
        self.statusBar.addPermanentWidget(self.mem_label)
        self.statusBar.addPermanentWidget(self.disk_label)
        
        # Timer for updating system info
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system_info)
        self.timer.start(2000)

    def update_system_info(self):
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        self.cpu_label.setText(f"CPU: {cpu_usage}%")
        self.mem_label.setText(f"RAM: {memory.percent}%")
        self.disk_label.setText(f"Disk: {disk.percent}%")

    def analyze_disk(self):
        disk_usage = {}
        for path, dirs, files in os.walk(os.path.expanduser("~")):
            try:
                size = sum(os.path.getsize(os.path.join(path, name)) for name in files)
                disk_usage[path] = size
            except:
                continue
        
        # Sonuçları göster
        dialog = QDialog(self)
        dialog.setWindowTitle("Disk Analizi")
        layout = QVBoxLayout()
        
        tree = QTreeWidget()
        tree.setHeaderLabels(["Konum", "Boyut"])
        
        for path, size in sorted(disk_usage.items(), key=lambda x: x[1], reverse=True)[:50]:
            item = QTreeWidgetItem()
            item.setText(0, path)
            item.setText(1, self.format_size(size))
            tree.addTopLevelItem(item)
        
        layout.addWidget(tree)
        dialog.setLayout(layout)
        dialog.resize(600, 400)
        dialog.exec_()

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def manage_startup(self):
        startup_dir = os.path.expanduser('~/.config/autostart')
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Başlangıç Uygulamaları")
        layout = QVBoxLayout()
        
        list_widget = QListWidget()
        
        if os.path.exists(startup_dir):
            for item in os.listdir(startup_dir):
                if item.endswith('.desktop'):
                    list_widget.addItem(item)
        
        layout.addWidget(list_widget)
        
        button_layout = QHBoxLayout()
        remove_btn = QPushButton("Kaldır")
        remove_btn.clicked.connect(lambda: self.remove_startup(list_widget.currentItem().text()))
        button_layout.addWidget(remove_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec_()

    def remove_startup(self, item):
        if item:
            startup_file = os.path.join(os.path.expanduser('~/.config/autostart'), item)
            try:
                os.remove(startup_file)
                QMessageBox.information(self, "Başarılı", "Başlangıç uygulaması kaldırıldı.")
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Kaldırma işlemi başarısız: {str(e)}")

    def manage_services(self):
        self.service_manager = ServiceManager()
        self.service_manager.show()

    def save_report(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Raporu Kaydet", "", "Text Files (*.txt)")
        if filename:
            with open(filename, 'w') as f:
                f.write(f"Sistem Temizlik Raporu - {datetime.now()}\n\n")
                f.write(self.result_text.toPlainText())

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Sol panel güncelleme
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setStyleSheet(CLEANUP_OPTIONS_STYLE)
        
        # Başlık
        title = QLabel("🧹 Temizlik Seçenekleri")
        title.setStyleSheet("""
            font-size: 16px;
            color: #2196F3;
            font-weight: bold;
            padding: 10px;
        """)
        left_layout.addWidget(title)
        
        # Tümünü Seç/Kaldır butonu
        select_all_btn = QPushButton("✓ Tümünü Seç/Kaldır")
        select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        select_all_btn.clicked.connect(self.toggle_all_items)
        left_layout.addWidget(select_all_btn)
        
        # TreeWidget
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setSelectionMode(QAbstractItemView.MultiSelection)
        self.tree.setAnimated(True)
        self.tree.setIndentation(20)
        left_layout.addWidget(self.tree)
        
        # Kategori ikonları
        category_icons = {
            "Sistem": "🔧",
            "Tarayıcılar": "🌐",
            "Uygulamalar": "📱"
        }
        
        # Alt öğe ikonları
        item_icons = {
            "Önbellek": "📁",
            "Geçici Dosyalar": "🗑️",
            "Paket Önbelleği": "📦",
            "Eski Kernel Dosyaları": "💽",
            "Günlük Dosyaları": "📄",
            "Chrome Önbelleği": "🌐",
            "Firefox Önbelleği": "🦊",
            "Opera Önbelleği": "🔴",
            "İndirilenler Geçmişi": "⬇️",
            "Uygulama Önbelleği": "💾",
            "Thumbnail Önbelleği": "🖼️",
            "Apt Önbelleği": "📦",
            "Snap Önbelleği": "📦",
            "Flatpak Önbelleği": "📦",
            "Çöp Kutusu": "🗑️"  # Yeni eklendi
        }

        # Kategorileri oluştur
        self.items = {}
        for category, items in self.categories.items():
            cat_item = QTreeWidgetItem([f"{category_icons[category]} {category}"])
            cat_item.setFlags(cat_item.flags() | Qt.ItemIsUserCheckable)
            cat_item.setCheckState(0, Qt.Unchecked)
            self.tree.addTopLevelItem(cat_item)
            self.items[category] = cat_item
            
            for item in items:
                child = QTreeWidgetItem([f"{item_icons.get(item, '•')} {item}"])
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setCheckState(0, Qt.Unchecked)
                # Alt öğe rengi ve yazı tipi
                child.setForeground(0, QColor("#e0e0e0"))
                cat_item.addChild(child)

        # Sağ panel güncelleme
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_panel.setStyleSheet(INFO_PANEL_STYLE)
        
        # Sistem bilgileri
        info_group = QGroupBox("Sistem Monitörü")
        info_layout = QVBoxLayout()
        
        # CPU Bilgileri
        cpu_widget = QWidget()
        cpu_layout = QHBoxLayout()
        
        cpu_icon = QLabel("🔲")
        cpu_icon.setStyleSheet("font-size: 16px;")
        
        cpu_labels = QVBoxLayout()
        cpu_header = QLabel("CPU Kullanımı")
        cpu_header.setProperty("type", "header")
        
        self.cpu_usage_label = QLabel()
        self.cpu_usage_label.setProperty("type", "value")
        
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setProperty("type", "cpu")
        self.cpu_bar.setTextVisible(False)
        
        cpu_labels.addWidget(cpu_header)
        cpu_labels.addWidget(self.cpu_usage_label)
        cpu_labels.addWidget(self.cpu_bar)
        
        cpu_layout.addWidget(cpu_icon)
        cpu_layout.addLayout(cpu_labels)
        cpu_widget.setLayout(cpu_layout)
        
        # RAM Bilgileri
        ram_widget = QWidget()
        ram_layout = QHBoxLayout()
        
        ram_icon = QLabel("💾")
        ram_icon.setStyleSheet("font-size: 16px;")
        
        ram_labels = QVBoxLayout()
        ram_header = QLabel("RAM Kullanımı")
        ram_header.setProperty("type", "header")
        
        self.memory_usage_label = QLabel()
        self.memory_usage_label.setProperty("type", "value")
        
        self.ram_bar = QProgressBar()
        self.ram_bar.setProperty("type", "ram")
        self.ram_bar.setTextVisible(False)
        
        ram_labels.addWidget(ram_header)
        ram_labels.addWidget(self.memory_usage_label)
        ram_labels.addWidget(self.ram_bar)
        
        ram_layout.addWidget(ram_icon)
        ram_layout.addLayout(ram_labels)
        ram_widget.setLayout(ram_layout)
        
        # Disk Bilgileri
        disk_widget = QWidget()
        disk_layout = QHBoxLayout()
        
        disk_icon = QLabel("💿")
        disk_icon.setStyleSheet("font-size: 16px;")
        
        disk_labels = QVBoxLayout()
        disk_header = QLabel("Disk Kullanımı")
        disk_header.setProperty("type", "header")
        
        self.disk_usage_label = QLabel()
        self.disk_usage_label.setProperty("type", "value")
        
        self.disk_bar = QProgressBar()
        self.disk_bar.setProperty("type", "disk")
        self.disk_bar.setTextVisible(False)
        
        disk_labels.addWidget(disk_header)
        disk_labels.addWidget(self.disk_usage_label)
        disk_labels.addWidget(self.disk_bar)
        
        disk_layout.addWidget(disk_icon)
        disk_layout.addLayout(disk_labels)
        disk_widget.setLayout(disk_layout)
        
        # Widget'ları grup layout'a ekle
        info_layout.addWidget(cpu_widget)
        info_layout.addWidget(ram_widget)
        info_layout.addWidget(disk_widget)
        
        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)

        # İlerleme çubuğu 
        self.progress = QProgressBar()
        self.progress.setTextVisible(True)
        right_layout.addWidget(self.progress)
        
        # Butonlar
        button_layout = QVBoxLayout()
        
        clean_btn = QPushButton("🧹 Temizle")
        clean_btn.setMinimumHeight(40)
        clean_btn.clicked.connect(self.clean_selected)
        
        analyze_btn = QPushButton("🔍 Analiz Et")
        analyze_btn.setMinimumHeight(40)
        analyze_btn.clicked.connect(self.analyze_system)
        
        button_layout.addWidget(clean_btn)
        button_layout.addWidget(analyze_btn)
        right_layout.addLayout(button_layout)
        
        # Layout'ları ana pencereye ekle
        layout.addWidget(left_panel, stretch=2)
        layout.addWidget(right_panel, stretch=1)
        
        # Timer for system info updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system_info)
        self.timer.start(2000)
        self.update_system_info()

    def toggle_all_items(self):
        """Tüm öğeleri seç/kaldır ve kategorileri genişlet"""
        # Mevcut durumu kontrol et
        state = Qt.Checked if self.items["Sistem"].checkState(0) == Qt.Unchecked else Qt.Unchecked
        
        # Tüm kategorileri ve alt öğeleri güncelle
        for category in self.items.values():
            # Kategoriyi genişlet/daralt
            if state == Qt.Checked:
                self.tree.expandItem(category)  # Kategoriyi genişlet
            else:
                self.tree.collapseItem(category)  # Kategoriyi daralt
                
            # Kategori durumunu güncelle    
            category.setCheckState(0, state)
            
            # Alt öğeleri güncelle
            for i in range(category.childCount()):
                child = category.child(i)
                child.setCheckState(0, state)

    def update_system_info(self):
        # CPU kullanımı
        cpu_usage = psutil.cpu_percent()
        self.cpu_usage_label.setText(f"{cpu_usage}%")
        self.cpu_bar.setValue(int(cpu_usage))
        
        # RAM kullanımı
        memory = psutil.virtual_memory()
        total_ram = memory.total / (1024**3)
        used_ram = memory.used / (1024**3)
        self.memory_usage_label.setText(f"{used_ram:.1f}GB / {total_ram:.1f}GB")
        self.ram_bar.setValue(int(memory.percent))
        
        # Disk kullanımı
        disk = psutil.disk_usage('/')
        total_disk = disk.total / (1024**3)
        used_disk = disk.used / (1024**3)
        free_disk = disk.free / (1024**3)
        self.disk_usage_label.setText(f"{used_disk:.1f}GB / {total_disk:.1f}GB")
        self.disk_bar.setValue(int(disk.percent))

    def clean_item(self, item_name):
        """Seçilen öğeyi temizler ve temizlenen boyutu döndürür"""
        try:
            cleaned_size = 0
            home = os.path.expanduser("~")
            
            cleanup_paths = {
                "Önbellek": [
                    "/var/cache/",  # Sistem cache
                    "/tmp/cache/"   # Geçici cache
                    # home/.cache kaldırıldı
                ],
                "Geçici Dosyalar": [
                    "/tmp/",
                    f"{home}/.local/share/Trash/files/",
                    f"{home}/.local/share/Trash/info/"
                ],
                "Paket Önbelleği": [
                    "/var/cache/apt/archives/",
                    "/var/cache/apt/pkgcache.bin",
                    "/var/cache/apt/srcpkgcache.bin"
                ],
                "Chrome Önbelleği": [
                    f"{home}/.cache/google-chrome/Default/Cache/",
                    f"{home}/.cache/google-chrome/Default/Code Cache/",
                    f"{home}/.config/google-chrome/Default/Application Cache/"
                ],
                "Firefox Önbelleği": [
                    f"{home}/.cache/mozilla/firefox/",
                    f"{home}/.mozilla/firefox/*.default/cache2/"
                ],
                "Opera Önbelleği": [
                    f"{home}/.cache/opera/",
                    f"{home}/.config/opera/Cache/"
                ],
                "Thumbnail Önbelleği": [
                    f"{home}/.cache/thumbnails/",
                    f"{home}/.thumbnails/"
                ],
                "Apt Önbelleği": [
                    "/var/cache/apt/archives/",
                    "/var/lib/apt/lists/"
                ],
                "Snap Önbelleği": [
                    "/var/lib/snapd/cache/",
                    "/var/cache/snapd/"
                ],
                "Flatpak Önbelleği": [
                    f"{home}/.var/app/*/cache/",
                    f"{home}/.cache/flatpak/"
                ],
                "Eski Kernel Dosyaları": [
                    "/boot/vmlinuz-*-old",
                    "/boot/initrd.img-*-old",
                    "/lib/modules/*-old"
                ],
                "Günlük Dosyaları": [
                    "/var/log/*.log",
                    "/var/log/*.log.*",
                    f"{home}/.local/share/xorg/",
                    "/var/log/apt/"
                ],
                "Çöp Kutusu": [
                    f"{os.path.expanduser('~')}/.local/share/Trash/files/",
                    f"{os.path.expanduser('~')}/.local/share/Trash/info/",
                    "/root/.local/share/Trash/files/",
                    "/root/.local/share/Trash/info/"
                ]
            }
            
            if item_name in cleanup_paths:
                for path_pattern in cleanup_paths[item_name]:
                    try:
                        # Home/.cache dizini kontrolü
                        if f"{home}/.cache" in path_pattern and os.path.dirname(path_pattern) == f"{home}/.cache":
                            continue  # Ana .cache dizinini atla
                            
                        # Diğer temizlik işlemleri
                        if '*' in path_pattern:
                            import glob
                            paths = glob.glob(path_pattern)
                        else:
                            paths = [path_pattern]
                            
                        for path in paths:
                            if os.path.exists(path):
                                # Dizin boyutunu hesapla
                                if os.path.isfile(path):
                                    size = os.path.getsize(path)
                                else:
                                    size = sum(os.path.getsize(os.path.join(dirpath,filename))
                                             for dirpath, dirnames, filenames in os.walk(path)
                                             for filename in filenames)
                                cleaned_size += size
                                
                                # Temizlik işlemi
                                try:
                                    if os.path.isfile(path):
                                        os.remove(path)
                                    else:
                                        shutil.rmtree(path, ignore_errors=True)
                                        os.makedirs(path, exist_ok=True)
                                except PermissionError:
                                    # Sudo ile tekrar dene
                                    if os.path.isfile(path):
                                        os.system(f'pkexec rm -f "{path}"')
                                    else:
                                        os.system(f'pkexec rm -rf "{path}"')
                                        os.system(f'pkexec mkdir -p "{path}"')
                    except Exception as e:
                        logging.error(f"Temizlik hatası ({path_pattern}): {str(e)}")
                        continue
            
            return cleaned_size
            
        except Exception as e:
            logging.error(f"Temizlik hatası ({item_name}): {str(e)}")
            return 0

    def update_progress(self, value, maximum=100):
        """Progress bar'ı günceller"""
        self.progress.setMaximum(maximum)
        self.progress.setValue(value)
        QApplication.processEvents()

    def analyze_system(self):
        """Sistem analizi yapar"""
        try:
            total_items = sum(category.childCount() for category in self.items.values())
            current_item = 0
            total_size = 0
            
            self.update_progress(0, total_items)
            
            for category in self.items.values():
                for i in range(category.childCount()):
                    child = category.child(i)
                    item_name = child.text(0).split(" ")[1]  # İkon karakterini kaldır
                    
                    try:
                        # Boyut hesaplama
                        size = self.get_cleanup_size(item_name)
                        readable_size = self.format_size(size)
                        
                        # Öğe metnini güncelle
                        child.setText(0, f"{child.text(0).split(' ')[0]} {item_name} ({readable_size})")
                        
                        total_size += size
                        current_item += 1
                        self.update_progress(current_item, total_items)
                        
                    except Exception as e:
                        logging.error(f"Analiz hatası ({item_name}): {str(e)}")
                        continue
            
            # Sonuçları göster            
            if total_size > 0:
                QMessageBox.information(self, "Analiz Tamamlandı", 
                                      f"Toplam temizlenebilir alan: {self.format_size(total_size)}")
            else:
                QMessageBox.warning(self, "Analiz Tamamlandı", 
                                  "Temizlenebilir dosya bulunamadı!")
                                  
            self.update_progress(0)
            
        except Exception as e:
            logging.error(f"Analiz hatası: {str(e)}")
            self.update_progress(0)
            QMessageBox.critical(self, "Hata", f"Analiz sırasında hata: {str(e)}")

    def format_size(self, size):
        """Boyutu okunabilir formata çevirir"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def clean_selected(self):
        """Seçili öğeleri temizler"""
        if self.cleanup_running:
            return

        self.cleanup_running = True
        self.progress.setMaximum(0)

        def cleanup_thread():
            try:
                total_size = 0
                selected_items = []
                
                # Seçili öğeleri topla
                for category in self.items.values():
                    for i in range(category.childCount()):
                        child = category.child(i)
                        if child.checkState(0) == Qt.Checked:
                            item_name = child.text(0).split(" ")[1]  # İkon karakterini kaldır
                            selected_items.append(item_name)

                if not selected_items:
                    self.error_occurred.emit("Lütfen temizlenecek öğeleri seçin!")
                    return

                total_items = len(selected_items)
                self.progress_updated.emit(0, total_items)

                for i, item in enumerate(selected_items):
                    try:
                        size = self.clean_item(item)
                        if size > 0:
                            total_size += size
                            logging.info(f"{item}: {size/1024/1024:.1f} MB temizlendi")
                        self.progress_updated.emit(i + 1, total_items)
                    except Exception as e:
                        logging.error(f"{item} temizlenirken hata: {str(e)}")
                        continue

                self.total_space_cleaned = total_size
                
                if total_size > 0:
                    self.process_finished.emit()
                    logging.info(f"Toplam temizlenen: {total_size/1024/1024:.1f} MB")
                else:
                    self.error_occurred.emit("Temizlenecek dosya bulunamadı!")

            except Exception as e:
                self.error_occurred.emit(f"Temizlik hatası: {str(e)}")
                logging.error(f"Temizlik hatası: {str(e)}")
            finally:
                self.cleanup_running = False
                self.progress.setMaximum(100)
                self.progress.setValue(0)

        Thread(target=cleanup_thread).start()

    def get_cleanup_size(self, item_name):
        """Temizlenebilecek boyutu hesaplar"""
        try:
            total_size = 0
            home = os.path.expanduser("~")
            
            cleanup_paths = {
                "Önbellek": [
                    "/var/cache/",
                    f"{home}/.cache/",
                    "/tmp/cache/"
                ],
                "Geçici Dosyalar": [
                    "/tmp/",
                    f"{home}/.local/share/Trash/files/",
                    f"{home}/.local/share/Trash/info/"
                ],
                "Paket Önbelleği": [
                    "/var/cache/apt/archives/",
                    "/var/cache/apt/pkgcache.bin",
                    "/var/cache/apt/srcpkgcache.bin"
                ],
                "Chrome Önbelleği": [
                    f"{home}/.cache/google-chrome/Default/Cache/",
                    f"{home}/.cache/google-chrome/Default/Code Cache/",
                    f"{home}/.config/google-chrome/Default/Application Cache/"
                ],
                "Firefox Önbelleği": [
                    f"{home}/.cache/mozilla/firefox/",
                    f"{home}/.mozilla/firefox/*.default/cache2/"
                ],
                "Opera Önbelleği": [
                    f"{home}/.cache/opera/",
                    f"{home}/.config/opera/Cache/"
                ],
                "Thumbnail Önbelleği": [
                    f"{home}/.cache/thumbnails/",
                    f"{home}/.thumbnails/"
                ],
                "Apt Önbelleği": [
                    "/var/cache/apt/archives/",
                    "/var/lib/apt/lists/"
                ],
                "Snap Önbelleği": [
                    "/var/lib/snapd/cache/",
                    "/var/cache/snapd/"
                ],
                "Flatpak Önbelleği": [
                    f"{home}/.var/app/*/cache/",
                    f"{home}/.cache/flatpak/"
                ],
                "Eski Kernel Dosyaları": [
                    "/boot/vmlinuz-*-old",
                    "/boot/initrd.img-*-old",
                    "/lib/modules/*-old"
                ],
                "Günlük Dosyaları": [
                    "/var/log/*.log",
                    "/var/log/*.log.*",
                    f"{home}/.local/share/xorg/",
                    "/var/log/apt/"
                ],
                "Çöp Kutusu": [
                    f"{os.path.expanduser('~')}/.local/share/Trash/files/",
                    f"{os.path.expanduser('~')}/.local/share/Trash/info/",
                    "/root/.local/share/Trash/files/",
                    "/root/.local/share/Trash/info/"
                ]
            }
            
            if item_name in cleanup_paths:
                for path_pattern in cleanup_paths[item_name]:
                    try:
                        if '*' in path_pattern:
                            import glob
                            paths = glob.glob(path_pattern)
                        else:
                            paths = [path_pattern]
                            
                        for path in paths:
                            if os.path.exists(path):
                                if os.path.isfile(path):
                                    total_size += os.path.getsize(path)
                                else:
                                    total_size += sum(os.path.getsize(os.path.join(dirpath,filename))
                                                    for dirpath, dirnames, filenames in os.walk(path)
                                                    for filename in filenames)
                    except Exception as e:
                        logging.error(f"Boyut hesaplama hatası ({path_pattern}): {str(e)}")
                        continue
            
            return total_size
            
        except Exception as e:
            logging.error(f"Boyut hesaplama hatası ({item_name}): {str(e)}")
            return 0

    def show_cleanup_summary(self):
        msg = QMessageBox()
        msg.setStyleSheet(MSGBOX_STYLE)
        msg.setWindowTitle("Temizlik Tamamlandı")
        msg.setText(f"Toplam {self.total_space_cleaned/1024/1024:.1f} MB alan temizlendi.")
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def setup_logging(self):
        """Log sistemi kurulumu"""
        try:
            log_dir = os.path.expanduser("~/.alsc/logs")
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, "alsc.log")
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file),
                    logging.StreamHandler()
                ]
            )
            logging.info("Log sistemi başlatıldı")
        except Exception as e:
            print(f"Log sistemi başlatılamadı: {e}")

    def check_permissions(self, path):
        """Dosya/dizin izinlerini kontrol eder"""
        try:
            return os.access(path, os.W_OK)
        except:
            return False

    def get_size_formatted(self, size_bytes):
        """Boyutu okunabilir formata çevirir"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def run_with_privileges(self, cmd):
        """Yönetici hakları gerektiren komutları çalıştırır"""
        try:
            if os.geteuid() != 0:
                cmd = f"pkexec {cmd}"
            return check_output(cmd.split(), stderr=PIPE)
        except Exception as e:
            self.error_occurred.emit(str(e))
            return None

    def save_settings(self):
        try:
            settings = {
                'window_geometry': self.saveGeometry().toBase64().data().decode(),
                'window_state': self.saveState().toBase64().data().decode(),
                'selected_items': self.get_selected_items(),
                'last_saved': datetime.now().isoformat()
            }
            
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
            
        except Exception as e:
            self.show_error("Ayar Kaydetme Hatası", str(e))

    def load_settings(self):
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                
                if 'window_geometry' in settings:
                    self.restoreGeometry(QByteArray.fromBase64(settings['window_geometry'].encode()))
                if 'window_state' in settings:
                    self.restoreState(QByteArray.fromBase64(settings['window_state'].encode()))
                if 'selected_items' in settings:
                    self.set_selected_items(settings['selected_items'])
                    
        except Exception as e:
            logging.error(f"Ayarlar yüklenirken hata: {str(e)}")

    def get_selected_items(self):
        selected = []
        for category in self.items.values():
            for i in range(category.childCount()):
                child = category.child(i)
                if child.checkState(0) == Qt.Checked:
                    selected.append(child.text(0))
        return selected

    def load_selected_items(self, items):
        for category in self.items.values():
            for i in range(category.childCount()):
                child = category.child(i)
                if child.text(0) in items:
                    child.setCheckState(0, Qt.Checked)

    def show_error_message(self, message):
        """Hata mesajlarını gösterir"""
        self.show_error("Hata", message)

    def show_error(self, title, message):
        msg = QMessageBox()
        msg.setStyleSheet(MSGBOX_STYLE)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

    def show_info(self, title, message):
        msg = QMessageBox()
        msg.setStyleSheet(MSGBOX_STYLE)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

    def on_process_finished(self):
        """İşlem tamamlandığında çağrılır"""
        self.progress.setMaximum(100)
        self.progress.setValue(100)
        self.show_cleanup_summary()
        self.update_system_info()

    def set_selected_items(self, items):
        self.selected_items = items
        
    def create_startup_manager(self):
        startup_widget = QWidget()
        layout = QVBoxLayout()
        
        # Tablo
        self.startup_table = QTableWidget()
        self.startup_table.setColumnCount(3)
        self.startup_table.setHorizontalHeaderLabels(["Program", "Yol", "Durum"])
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.add_startup_button = QPushButton("Uygulama Ekle")
        self.activate_button = QPushButton("Aktif Et")
        self.deactivate_button = QPushButton("Pasif Et")
        self.remove_button = QPushButton("Kaldır")
        
        button_layout.addWidget(self.add_startup_button)
        button_layout.addWidget(self.activate_button)
        button_layout.addWidget(self.deactivate_button)
        button_layout.addWidget(self.remove_button)
        
        # Sinyal bağlantıları
        self.add_startup_button.clicked.connect(self.add_startup_app)
        self.activate_button.clicked.connect(lambda: self.toggle_startup_item(True))
        self.deactivate_button.clicked.connect(lambda: self.toggle_startup_item(False))
        self.remove_button.clicked.connect(self.remove_startup_item)
        
        layout.addWidget(self.startup_table)
        layout.addLayout(button_layout)
        
        startup_widget.setLayout(layout)
        self.startup_manager = StartupManager()
        self.load_startup_items()
        return startup_widget

    def load_startup_items(self):
        self.startup_manager = StartupManager()
        items = self.startup_manager.get_startup_items()
        self.startup_table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            self.startup_table.setItem(row, 0, QTableWidgetItem(item["name"]))
            self.startup_table.setItem(row, 1, QTableWidgetItem(item["path"]))
            self.startup_table.setItem(row, 2, QTableWidgetItem("Aktif" if item["enabled"] else "Pasif"))

    def add_startup_app(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Başlangıç Uygulaması Seç",
            os.path.expanduser("~"),
            "Tüm Dosyalar (*)"
        )
        if file_path:
            name = os.path.splitext(os.path.basename(file_path))[0]
            if self.startup_manager.add_startup_item(name, file_path):
                self.load_startup_items()
                self.show_info("Başarılı", "Uygulama başlangıca eklendi.")
            else:
                self.show_error("Hata", "Uygulama eklenirken hata oluştu.")

    def remove_startup_item(self):
        selected = self.startup_table.selectedItems()
        if selected:
            row = selected[0].row()
            name = self.startup_table.item(row, 0).text()
            if self.startup_manager.remove_startup_item(name):
                self.load_startup_items()
                QMessageBox.information(self, "Başarılı", "Uygulama başlangıçtan kaldırıldı.")
            else:
                QMessageBox.warning(self, "Hata", "Uygulama kaldırılırken hata oluştu.")

    def toggle_startup_item(self, enable):
        selected = self.startup_table.selectedItems()
        if selected:
            row = selected[0].row()
            name = self.startup_table.item(row, 0).text()
            if self.startup_manager.toggle_startup_item(name, enable):
                status = "aktif" if enable else "pasif"
                QMessageBox.information(self, "Başarılı", f"Uygulama {status} edildi.")
                self.load_startup_items()
            else:
                QMessageBox.warning(self, "Hata", "İşlem başarısız oldu.")

    def show_optimization_results(self, before_memory, after_memory):
        try:
            # Sonuçları hesapla
            freed_memory = round(before_memory - after_memory, 2)
            available_ram = round(psutil.virtual_memory().available/1024/1024/1024, 2)
            used_percent = round(psutil.virtual_memory().percent, 1)
            
            # Mesaj detaylarını hazırla
            details = f"""RAM Optimizasyonu Tamamlandı!

📊 Optimizasyon Sonuçları:
---------------------------
• Temizlenen RAM: {freed_memory} GB
• Kullanılabilir RAM: {available_ram} GB
• RAM Kullanım Oranı: %{used_percent}

✅ Yapılan İşlemler:
---------------------------
• Kernel Önbellekleri Temizlendi
• SWAP Alanı Optimize Edildi
• Sistem Parametreleri İyileştirildi
• Önbellekler Temizlendi
• Gereksiz Servisler Durduruldu
• RAM Kullanan Süreçler Optimize Edildi"""

            # MessageBox göster
            msg = QMessageBox()
            msg.setStyleSheet(MSGBOX_STYLE)
            msg.setWindowTitle("Optimizasyon Tamamlandı")
            msg.setText(details)
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
            
        except Exception as e:
            logging.error(f"Sonuç gösterme hatası: {str(e)}")

    def clear_memory(self):
        if hasattr(self, 'cleanup_running') and self.cleanup_running:
            return
            
        self.cleanup_running = True
        TOTAL_STEPS = 100
    
        # Ana thread'de progress barı ayarla
        QMetaObject.invokeMethod(self.progress, "setMaximum", 
                           Qt.QueuedConnection,
                           Q_ARG(int, TOTAL_STEPS))
        QMetaObject.invokeMethod(self.progress, "setValue",
                           Qt.QueuedConnection, 
                           Q_ARG(int, 0))

        # Başlangıç mesajı
        start_msg = QMessageBox()
        start_msg.setStyleSheet(MSGBOX_STYLE)
        start_msg.setWindowTitle("RAM Optimizasyonu")
        start_msg.setText("RAM optimizasyonu başlatılıyor...\n\nBu işlem birkaç dakika sürebilir.")
        start_msg.setIcon(QMessageBox.Information)
        start_msg.show()
        QTimer.singleShot(2000, start_msg.close)

        def cleanup_thread():
            try:
                before_memory = psutil.virtual_memory().used / (1024 * 1024 * 1024)
                
                steps = [
                    ("Kernel önbellekleri temizleniyor", 
                     'sync && echo 3 | pkexec tee /proc/sys/vm/drop_caches', 10),
                    ("SWAP optimize ediliyor", 
                     'pkexec swapoff -a && pkexec swapon -a', 20),
                    ("OOM killer ayarlanıyor",
                     'echo 60 | pkexec tee /proc/sys/vm/swappiness', 30),
                    ("Disk önbellek optimizasyonu",
                     'echo 1500 | pkexec tee /proc/sys/vm/vfs_cache_pressure', 40),
                    ("Sayfa birleştirme etkinleştiriliyor",
                     'echo 1 | pkexec tee /proc/sys/vm/compaction_proactiveness', 50),
                    ("Bellek sıkıştırma optimizasyonu",
                     'echo 100 | pkexec tee /proc/sys/vm/watermark_scale_factor', 60),
                ]
                
                for msg, cmd, progress in steps:
                    # Status bar güvenli güncelleme
                    QMetaObject.invokeMethod(self.status_bar, "showMessage",
                                       Qt.QueuedConnection,
                                       Q_ARG(str, msg))
                    
                    # Progress bar güvenli güncelleme 
                    QMetaObject.invokeMethod(self.progress, "setValue",
                                       Qt.QueuedConnection,
                                       Q_ARG(int, progress))
                                       
                    os.system(cmd)

                # Önbellek temizleme
                cache_paths = ["~/.cache/*", "/tmp/*", "/var/tmp/*"]
                for path in cache_paths:
                    os.system(f'rm -rf {os.path.expanduser(path)}')
                    
                QMetaObject.invokeMethod(self.progress, "setValue",
                                   Qt.QueuedConnection,
                                   Q_ARG(int, 70))

                # Servisleri durdur
                services = ["bluetooth", "cups", "avahi-daemon"]
                for service in services:
                    os.system(f'pkexec systemctl stop {service} 2>/dev/null')
                    
                QMetaObject.invokeMethod(self.progress, "setValue", 
                                   Qt.QueuedConnection,
                                   Q_ARG(int, 80))

                # RAM süreçlerini optimize et
                for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                    try:
                        if proc.info['memory_percent'] > 5.0:
                            os.system(f'pkexec ionice -c 3 -p {proc.info["pid"]}')
                            os.system(f'pkexec renice 19 -p {proc.info["pid"]}')
                    except:
                        continue

                QMetaObject.invokeMethod(self.progress, "setValue",
                                   Qt.QueuedConnection, 
                                   Q_ARG(int, 90))

                # Sonuçları hesapla
                after_memory = psutil.virtual_memory().used / (1024 * 1024 * 1024)
                freed_memory = round(before_memory - after_memory, 2)
                available_ram = round(psutil.virtual_memory().available/1024/1024/1024, 2)
                
                details = f"""RAM Optimizasyonu Tamamlandı
                
                • Temizlenen RAM: {freed_memory} GB
                • Kullanılabilir RAM: {available_ram} GB
                • Önbellekler Temizlendi
                • SWAP Optimize Edildi  
                • Sistem Parametreleri İyileştirildi
                • Gereksiz Hizmetler Durduruldu
                • Süreçler Optimize Edildi"""

                # Son güncellemeler (ana thread'de)
                QMetaObject.invokeMethod(self.progress, "setValue",
                                   Qt.QueuedConnection,
                                   Q_ARG(int, TOTAL_STEPS))
                                   
                QMetaObject.invokeMethod(self.status_bar, "showMessage",
                                   Qt.QueuedConnection,
                                   Q_ARG(str, f"RAM optimizasyonu tamamlandı. Kullanılabilir RAM: {available_ram} GB"))

                # Bilgi mesajı ana thread'de göster
                QTimer.singleShot(0, lambda: self.show_info("Başarılı", details))
                
                logging.info(f"RAM optimizasyonu başarılı. Temizlenen: {freed_memory} GB")

                # Thread-safe sonuç gösterimi
                QTimer.singleShot(0, lambda: self.show_optimization_dialog(before_memory, after_memory))

            except Exception as e:
                logging.error(f"RAM optimizasyon hatası: {str(e)}")
                QTimer.singleShot(0, lambda: self.show_error("Hata", str(e)))
                
            finally:
                self.cleanup_running = False

        Thread(target=cleanup_thread).start()

    def show_optimization_dialog(self, before_memory, after_memory):
        try:
            # Sonuçları hesapla
            freed_memory = round(before_memory - after_memory, 2)
            available_ram = round(psutil.virtual_memory().available/1024/1024/1024, 2)
            used_percent = round(psutil.virtual_memory().percent, 1)
            
            details = f"""🔄 RAM Optimizasyonu Tamamlandı!

📊 Optimizasyon Sonuçları:
---------------------------
• Temizlenen RAM: {freed_memory} GB
• Kullanılabilir RAM: {available_ram} GB
• RAM Kullanım Oranı: %{used_percent}

✅ Yapılan İşlemler:
---------------------------
• Kernel Önbellekleri Temizlendi
• SWAP Alanı Optimize Edildi
• OOM Killer Ayarlandı
• Disk Önbellekleri Optimize Edildi
• Sayfa Birleştirme Etkinleştirildi
• Bellek Sıkıştırma Optimize Edildi
• Sistem Önbellekleri Temizlendi
• Gereksiz Servisler Durduruldu
• RAM Kullanan Süreçler Optimize Edildi"""

            msg = QMessageBox()
            msg.setStyleSheet(MSGBOX_STYLE)
            msg.setWindowTitle("RAM Optimizasyonu Sonucu")
            msg.setText(details)
            msg.setIcon(QMessageBox.Information)
            msg.exec_()

        except Exception as e:
            logging.error(f"Optimizasyon sonuç gösterme hatası: {str(e)}")

class ServiceManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gelişmiş Servis Yöneticisi")
        self.setGeometry(100, 100, 900, 600)
        self.setup_logging()
        self.init_ui()
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1a1a1a;
                color: #e0e0e0;
            }
            
            QTableWidget {
                background-color: #2d2d2d;
                color: #e0e0e0;
                gridline-color: #3d3d3d;
                border: 1px solid #3d3d3d;
            }
            
            QTableWidget::item:selected {
                background-color: #404040;
            }
            
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                padding: 4px;
            }
            
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                color: #e0e0e0;
                padding: 5px 15px;
                border-radius: 3px;
            }
            
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            
            QPushButton:pressed {
                background-color: #454545;
            }
            
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                color: #e0e0e0;
                padding: 3px;
                border-radius: 2px;
            }
            
            QStatusBar {
                background-color: #2d2d2d;
                color: #e0e0e0;
            }
            
            QDialog {
                background-color: #1a1a1a;
                color: #e0e0e0;
            }
            
            QTextBrowser {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
            }
        """)

    def setup_logging(self):
        logging.basicConfig(
            filename='service_manager.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def init_ui(self):
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Üst toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        refresh_btn = QAction(QIcon.fromTheme("view-refresh"), "Yenile", self)
        refresh_btn.triggered.connect(self.refresh_services)
        toolbar.addAction(refresh_btn)
        
        # Arama kutusu
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Servis ara...")
        self.search_box.textChanged.connect(self.filter_services)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)
        
        # Tablo oluşturma
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Servis Adı", "Durum", "Bellek Kullanımı",
            "CPU Kullanımı", "Başlangıç Durumu", "İşlemler"
        ])
        
        # Sütun genişliklerini ayarla
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Servis adı
        header.setSectionResizeMode(1, QHeaderView.Fixed)    # Durum
        header.setSectionResizeMode(2, QHeaderView.Fixed)    # Bellek
        header.setSectionResizeMode(3, QHeaderView.Fixed)    # CPU
        header.setSectionResizeMode(4, QHeaderView.Fixed)    # Başlangıç
        header.setSectionResizeMode(5, QHeaderView.Fixed)    # İşlemler
        
        self.table.setColumnWidth(1, 100)  # Durum
        self.table.setColumnWidth(2, 120)  # Bellek
        self.table.setColumnWidth(3, 100)  # CPU
        self.table.setColumnWidth(4, 120)  # Başlangıç
        self.table.setColumnWidth(5, 300)  # İşlemler
        
        layout.addWidget(self.table)
        
        # Alt bilgi paneli
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Otomatik yenileme için zamanlayıcı
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_services)
        self.refresh_timer.start(30000)  # Her 30 saniyede bir yenile
        
        self.load_services()
        
    def load_services(self):
        try:
            cmd = "systemctl list-units --type=service --all"
            process = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
            output, error = process.communicate()
            
            services = []
            for line in output.decode().split('\n'):
                if '.service' in line:
                    services.append(line.split()[0].replace('.service', ''))
            
            self.table.setRowCount(len(services))
            for i, service in enumerate(services):
                self.update_service_row(i, service)
                
        except Exception as e:
            self.show_error("Servisler yüklenirken hata oluştu!", str(e))
            logging.error(f"Servis yükleme hatası: {str(e)}")
            
    def update_service_row(self, row, service):
        # Servis adı
        self.table.setItem(row, 0, QTableWidgetItem(service))
        
        # Servis durumu
        status = self.get_service_status(service)
        status_item = QTableWidgetItem(status)
        if status == "active":
            status_item.setForeground(QColor("#2ecc71"))  # Yeşil
        else:
            status_item.setForeground(QColor("#e74c3c"))  # Kırmızı
        self.table.setItem(row, 1, status_item)
        
        # Bellek kullanımı
        memory = self.get_service_memory(service)
        memory_item = QTableWidgetItem(memory)
        memory_item.setForeground(QColor("#3498db"))  # Mavi
        self.table.setItem(row, 2, memory_item)
        
        # CPU kullanımı
        cpu = self.get_service_cpu(service)
        cpu_item = QTableWidgetItem(cpu)
        cpu_item.setForeground(QColor("#f1c40f"))  # Sarı
        self.table.setItem(row, 3, cpu_item)
        
        # Boot durumu
        boot_status = self.get_boot_status(service)
        boot_item = QTableWidgetItem(boot_status)
        if boot_status == "enabled":
            boot_item.setForeground(QColor("#2ecc71"))
        else:
            boot_item.setForeground(QColor("#95a5a6"))
        self.table.setItem(row, 4, boot_item)
        
        # İşlem butonları
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(5, 2, 5, 2)
        btn_layout.setSpacing(5)
        
        toggle_btn = QPushButton("Başlat/Durdur")
        toggle_btn.setFixedWidth(90)
        toggle_btn.clicked.connect(lambda: self.toggle_service(service))
        
        restart_btn = QPushButton("Y.Başlat")
        restart_btn.setFixedWidth(70)
        restart_btn.clicked.connect(lambda: self.restart_service(service))
        
        info_btn = QPushButton("Bilgi")
        info_btn.setFixedWidth(60)
        info_btn.clicked.connect(lambda: self.show_service_info(service))
        
        # Butonların stilini ayarla
        for btn in [toggle_btn, restart_btn, info_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 3px;
                    font-size: 11px;
                }
            """)
            btn_layout.addWidget(btn)
        
        btn_widget.setLayout(btn_layout)
        self.table.setCellWidget(row, 5, btn_widget)
        
    def get_service_status(self, service):
        try:
            cmd = f"systemctl is-active {service}"
            process = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
            output, _ = process.communicate()
            return output.decode().strip()
        except:
            return "unknown"
            
    def get_service_memory(self, service):
        try:
            cmd = f"systemctl show {service} -p MemoryCurrent"
            process = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
            output, _ = process.communicate()
            memory_bytes = int(output.decode().split('=')[1])
            return f"{memory_bytes / 1024 / 1024:.1f} MB"
        except:
            return "N/A"
            
    def get_service_cpu(self, service):
        try:
            cmd = f"ps -p $(systemctl show {service} -p MainPID | cut -d'=' -f2) -o %cpu="
            process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
            output, _ = process.communicate()
            return f"{float(output.decode().strip()):.1f}%"
        except:
            return "N/A"
            
    def get_boot_status(self, service):
        try:
            cmd = f"systemctl is-enabled {service}"
            process = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
            output, _ = process.communicate()
            return output.decode().strip()
        except:
            return "unknown"
            
    def toggle_service(self, service):
        try:
            current_status = self.get_service_status(service)
            action = "stop" if current_status == "active" else "start"
            
            cmd = f"pkexec systemctl {action} {service}"
            process = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
            _, error = process.communicate()
            
            if process.returncode == 0:
                self.show_info("Başarılı", f"{service} servisi {action} işlemi başarılı")
                logging.info(f"{service} servisi {action} işlemi başarılı")
            else:
                raise Exception(error.decode())
                
        except Exception as e:
            self.show_error("Hata", f"Servis işlemi başarısız: {str(e)}")
            logging.error(f"Servis işlemi hatası: {str(e)}")
            
        self.refresh_services()
        
    def restart_service(self, service):
        try:
            cmd = f"pkexec systemctl restart {service}"
            process = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
            _, error = process.communicate()
            
            if process.returncode == 0:
                self.show_info("Başarılı", f"{service} servisi yeniden başlatıldı")
                logging.info(f"{service} servisi yeniden başlatıldı")
            else:
                raise Exception(error.decode())
                
        except Exception as e:
            self.show_error("Hata", f"Yeniden başlatma başarısız: {str(e)}")
            logging.error(f"Yeniden başlatma hatası: {str(e)}")
            
        self.refresh_services()
        
    def show_service_info(self, service):
        try:
            cmd = f"systemctl status {service}"
            process = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
            output, _ = process.communicate()
            
            info_dialog = QDialog(self)
            info_dialog.setWindowTitle(f"{service} Detayları")
            info_dialog.setMinimumSize(600, 400)
            
            layout = QVBoxLayout()
            text_browser = QTextBrowser()
            text_browser.setText(output.decode())
            layout.addWidget(text_browser)
            
            info_dialog.setLayout(layout)
            info_dialog.exec_()
            
        except Exception as e:
            self.show_error("Hata", f"Servis bilgileri alınamadı: {str(e)}")
            
    def filter_services(self):
        search_text = self.search_box.text().lower()
        for row in range(self.table.rowCount()):
            service_name = self.table.item(row, 0).text().lower()
            self.table.setRowHidden(row, search_text not in service_name)
            
    def refresh_services(self):
        self.load_services()
        self.status_bar.showMessage(f"Son güncelleme: {datetime.now().strftime('%H:%M:%S')}")
        
    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)
        
    def show_info(self, title, message):
        QMessageBox.information(self, title, message)

# ...existing code...

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemCleaner()
    
    # Uygulama ikonu ayarla
    if window.ICON_PATH:
        app_icon = QIcon(window.ICON_PATH)
        app.setWindowIcon(app_icon)
        window.setWindowIcon(app_icon)
    
    window.show()
    sys.exit(app.exec_())

