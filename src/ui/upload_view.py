from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QFrame
)
from PyQt5.QtCore import pyqtSignal, Qt
from src.utils.helpers import is_valid_file, get_file_type
import os
import logging

logger = logging.getLogger("MedicalApp.UploadView")

class UploadView(QWidget):
    """View to select or drag & drop PDF and image medical reports for processing."""
    
    file_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setup_ui()

    def setup_ui(self):
        """Creates the UI widgets for drag-and-drop upload."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QVBoxLayout()
        header = QLabel("Upload Report")
        header.setObjectName("HeaderLabel")
        header_layout.addWidget(header)
        
        subheader = QLabel("Select or drag a lab report (PDF, PNG, JPG, TIFF) to analyze")
        subheader.setObjectName("SubHeaderLabel")
        header_layout.addWidget(subheader)
        layout.addLayout(header_layout)
        
        # Drag & Drop Zone Frame
        self.drop_frame = QFrame()
        self.drop_frame.setObjectName("DashboardCard")
        self.drop_frame.setStyleSheet("""
            QFrame#DashboardCard {
                border: 2px dashed #38BDF8;
                border-radius: 16px;
                background-color: #F1F5F9;
            }
        """)
        
        drop_layout = QVBoxLayout(self.drop_frame)
        drop_layout.setAlignment(Qt.AlignCenter)
        drop_layout.setSpacing(15)
        
        # Visual Icon
        icon_label = QLabel("📥")
        icon_label.setStyleSheet("font-size: 56px; background: transparent;")
        icon_label.setAlignment(Qt.AlignCenter)
        drop_layout.addWidget(icon_label)
        
        # Description
        self.drop_label = QLabel("Drag & Drop File Here\n- OR -")
        self.drop_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #475569; background: transparent;")
        self.drop_label.setAlignment(Qt.AlignCenter)
        drop_layout.addWidget(self.drop_label)
        
        # Select Button
        btn_select = QPushButton("Browse Files")
        btn_select.clicked.connect(self.browse_files)
        btn_select.setFixedWidth(150)
        drop_layout.addWidget(btn_select, alignment=Qt.AlignCenter)
        
        # Formats list
        info_label = QLabel("Supported formats: PDF, PNG, JPG, JPEG, TIFF (Max size: 10MB)")
        info_label.setStyleSheet("font-size: 11px; color: #94A3B8; background: transparent;")
        info_label.setAlignment(Qt.AlignCenter)
        drop_layout.addWidget(info_label)
        
        layout.addWidget(self.drop_frame, stretch=1)

    def set_theme_colors(self, dark_mode: bool):
        """Updates dotted border based on light or dark modes."""
        if dark_mode:
            self.drop_frame.setStyleSheet("""
                QFrame#DashboardCard {
                    border: 2px dashed #0EA5E9;
                    border-radius: 16px;
                    background-color: #1E293B;
                }
            """)
            self.drop_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #94A3B8; background: transparent;")
        else:
            self.drop_frame.setStyleSheet("""
                QFrame#DashboardCard {
                    border: 2px dashed #38BDF8;
                    border-radius: 16px;
                    background-color: #F8FAFC;
                }
            """)
            self.drop_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #475569; background: transparent;")

    def browse_files(self):
        """Opens a file dialog for the user to select medical report files."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Medical Report",
            "",
            "Medical Reports (*.pdf *.png *.jpg *.jpeg *.tiff);;All Files (*)"
        )
        if file_path:
            self.process_selected_file(file_path)

    # --- Drag & Drop Event Handling ---

    def dragEnterEvent(self, event):
        """Checks if files are being dragged over the widget."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_frame.setStyleSheet(self.drop_frame.styleSheet() + "border: 2px dashed #10B981;") # Highlight green
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """Reverts the border styling when drag leaves."""
        # Refresh theme to restore style
        self.set_theme_colors(self.drop_frame.palette().color(self.drop_frame.backgroundRole()).lightness() < 128)

    def dropEvent(self, event):
        """Handles file drop event."""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.process_selected_file(file_path)

    def process_selected_file(self, file_path: str):
        """Validates the file path and registers it for analysis."""
        if not os.path.exists(file_path):
            QMessageBox.critical(self, "Error", "Selected file does not exist.")
            return

        if not is_valid_file(file_path):
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            ext = get_file_type(file_path)
            
            if ext not in ["pdf", "png", "jpg", "jpeg", "tiff"]:
                QMessageBox.critical(self, "Invalid File Type", 
                                     f"Unsupported file extension '.{ext}'. Please upload a PDF or image.")
            elif size_mb > 10.0:
                QMessageBox.critical(self, "File Too Large", 
                                     f"File size is {size_mb:.2f}MB, which exceeds the 10MB limit.")
            else:
                QMessageBox.critical(self, "Error", "Invalid report file.")
            return

        logger.info(f"File validated: {file_path}")
        self.file_selected.emit(file_path)
