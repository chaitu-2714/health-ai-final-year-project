from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QFileDialog, QMessageBox, QComboBox
)
from PyQt5.QtCore import pyqtSignal, Qt
from src.utils import get_config, save_config
import os
import logging

logger = logging.getLogger("MedicalApp.SettingsView")

class SettingsView(QWidget):
    """View allowing customization of OCR executable path and Ollama AI settings."""
    
    # Emits theme toggled signal to synchronize main window if changed
    config_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_values()

    def setup_ui(self):
        """Creates configuration input fields, browse dialog triggers, and buttons."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header_layout = QVBoxLayout()
        header = QLabel("Application Settings")
        header.setObjectName("HeaderLabel")
        header_layout.addWidget(header)
        
        subheader = QLabel("Configure offline dependencies, system paths, and local AI engines")
        subheader.setObjectName("SubHeaderLabel")
        header_layout.addWidget(subheader)
        layout.addLayout(header_layout)

        # Container Card
        card = QFrame()
        card.setObjectName("DashboardCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(15)

        # 1. Tesseract Section
        card_layout.addWidget(QLabel("Tesseract OCR Configurations", styleSheet="font-weight: bold; font-size: 14px; color: #0EA5E9;"))
        
        tess_box = QHBoxLayout()
        self.tess_input = QLineEdit()
        self.tess_input.setPlaceholderText(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
        tess_box.addWidget(self.tess_input)
        
        btn_browse_tess = QPushButton("Browse...")
        btn_browse_tess.setObjectName("SecondaryButton")
        btn_browse_tess.clicked.connect(self.browse_tesseract)
        tess_box.addWidget(btn_browse_tess)
        card_layout.addLayout(tess_box)
        card_layout.addWidget(QLabel("Enter the path to the 'tesseract.exe' file. Default: C:\\Program Files\\Tesseract-OCR\\tesseract.exe", styleSheet="font-size: 11px; color: #64748B;"))
        card_layout.addSpacing(10)

        # 2. Ollama Section
        card_layout.addWidget(QLabel("Local Ollama AI Settings", styleSheet="font-weight: bold; font-size: 14px; color: #0EA5E9;"))
        
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Ollama Server URL:", styleSheet="min-width: 120px;"))
        self.ollama_url_input = QLineEdit()
        self.ollama_url_input.setPlaceholderText("http://localhost:11434")
        url_layout.addWidget(self.ollama_url_input)
        card_layout.addLayout(url_layout)

        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Ollama Model Name:", styleSheet="min-width: 120px;"))
        self.ollama_model_input = QLineEdit()
        self.ollama_model_input.setPlaceholderText("gemma2:2b")
        model_layout.addWidget(self.ollama_model_input)
        card_layout.addLayout(model_layout)
        card_layout.addWidget(QLabel("Ollama must be running locally. Recommended models: 'gemma2:2b', 'llama3:8b', or 'llama3.2:3b'.", styleSheet="font-size: 11px; color: #64748B;"))
        card_layout.addSpacing(10)

        # Actions Row
        btn_box = QHBoxLayout()
        btn_reset = QPushButton("Reset Defaults")
        btn_reset.setObjectName("SecondaryButton")
        btn_reset.clicked.connect(self.reset_defaults)
        btn_box.addWidget(btn_reset)
        
        btn_box.addStretch()
        
        btn_save = QPushButton("Save Configurations")
        btn_save.clicked.connect(self.save_values)
        btn_box.addWidget(btn_save)
        
        card_layout.addLayout(btn_box)

        layout.addWidget(card, stretch=1)

    def load_values(self):
        """Loads properties from config.json."""
        config = get_config()
        self.tess_input.setText(config.get("tesseract_path", ""))
        self.ollama_url_input.setText(config.get("ollama_url", ""))
        self.ollama_model_input.setText(config.get("ollama_model", ""))

    def browse_tesseract(self):
        """Opens file dialog seeking the tesseract executable binary."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Tesseract Executable",
            "C:\\Program Files",
            "Executable Files (tesseract.exe);;All Files (*)"
        )
        if path:
            self.tess_input.setText(os.path.normpath(path))

    def save_values(self):
        """Validates options and persists settings to JSON."""
        tess_path = self.tess_input.text().strip()
        url = self.ollama_url_input.text().strip()
        model = self.ollama_model_input.text().strip()

        # Basic validations
        if tess_path and not os.path.exists(tess_path):
            QMessageBox.warning(self, "Warning", f"The Tesseract path '{tess_path}' does not exist. Verify the path is correct.")

        config = get_config()
        config["tesseract_path"] = tess_path
        config["ollama_url"] = url
        config["ollama_model"] = model

        success = save_config(config)
        if success:
            QMessageBox.information(self, "Success", "Configuration settings saved successfully.")
            self.config_updated.emit()
        else:
            QMessageBox.critical(self, "Error", "Failed to save configuration settings.")

    def reset_defaults(self):
        """Restores defaults."""
        confirm = QMessageBox.question(
            self,
            "Confirm Reset",
            "Are you sure you want to reset all configurations to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            from src.utils.helpers import DEFAULT_CONFIG
            save_config(DEFAULT_CONFIG)
            self.load_values()
            self.config_updated.emit()
            QMessageBox.information(self, "Success", "Settings reset to default values.")
