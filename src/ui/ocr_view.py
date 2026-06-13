from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QFrame, QSplitter, QProgressBar
)
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from PyQt5.QtGui import QPixmap, QImage
import fitz  # PyMuPDF
import os
import logging
from src.services.ocr_service import OCRService

logger = logging.getLogger("MedicalApp.OCRView")

class OCRWorker(QThread):
    """Asynchronous worker to run OpenCV pre-processing and Tesseract OCR."""
    finished = pyqtSignal(str, str)

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            # Perform extraction
            text = OCRService.extract(self.file_path)
            self.finished.emit(text, "")
        except Exception as e:
            logger.error(f"OCR Worker error: {e}")
            self.finished.emit("", str(e))

class OCRView(QWidget):
    """View showing the uploaded report preview and raw OCR text editor."""
    
    analysis_requested = pyqtSignal(str, str) # raw_text, file_path

    def __init__(self):
        super().__init__()
        self.file_path = None
        self.worker = None
        self.setup_ui()

    def setup_ui(self):
        """Creates splitter view for Image preview (left) and Text editor (right)."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_layout = QVBoxLayout()
        header = QLabel("Verify Text")
        header.setObjectName("HeaderLabel")
        header_layout.addWidget(header)
        
        self.subheader = QLabel("Verify and correct the extracted text before running the clinical analysis engine")
        self.subheader.setObjectName("SubHeaderLabel")
        header_layout.addWidget(self.subheader)
        layout.addLayout(header_layout)

        # Loading Progress Bar (Hidden by default)
        self.loading_widget = QWidget()
        loading_layout = QVBoxLayout(self.loading_widget)
        loading_layout.setContentsMargins(0, 0, 0, 0)
        
        self.loading_lbl = QLabel("⏳ Enhancing image quality and running Tesseract OCR...")
        self.loading_lbl.setStyleSheet("font-weight: bold; color: #0EA5E9;")
        loading_layout.addWidget(self.loading_lbl)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Infinite spinner mode
        self.progress_bar.setFixedHeight(8)
        loading_layout.addWidget(self.progress_bar)
        
        layout.addWidget(self.loading_widget)
        self.loading_widget.hide()

        # Splitter Layout (Left: Preview, Right: Editable Text)
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel (Preview Card)
        self.preview_card = QFrame()
        self.preview_card.setObjectName("DashboardCard")
        preview_layout = QVBoxLayout(self.preview_card)
        preview_layout.addWidget(QLabel("Document Preview", objectName="CardTitle"))
        
        self.img_label = QLabel("No Document Loaded")
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setStyleSheet("background-color: #E2E8F0; border-radius: 8px;")
        self.img_label.setMinimumWidth(250)
        preview_layout.addWidget(self.img_label, stretch=1)
        
        self.splitter.addWidget(self.preview_card)

        # Right Panel (Editable Text Card)
        text_card = QFrame()
        text_card.setObjectName("DashboardCard")
        text_layout = QVBoxLayout(text_card)
        text_layout.addWidget(QLabel("Raw Extracted Text (Editable)", objectName="CardTitle"))
        
        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("OCR text will appear here. You can manually edit or correct this text...")
        text_layout.addWidget(self.text_editor)
        
        self.splitter.addWidget(text_card)
        
        # Set splitter proportions
        self.splitter.setSizes([300, 500])
        layout.addWidget(self.splitter, stretch=1)

        # Footer Actions
        actions_layout = QHBoxLayout()
        self.btn_back = QPushButton("Upload Another File")
        self.btn_back.setObjectName("SecondaryButton")
        actions_layout.addWidget(self.btn_back)
        
        actions_layout.addStretch()
        
        self.btn_analyze = QPushButton("Run Clinical Health Analysis ➔")
        self.btn_analyze.clicked.connect(self.request_analysis)
        actions_layout.addWidget(self.btn_analyze)
        
        layout.addLayout(actions_layout)

    def set_theme_colors(self, dark_mode: bool):
        """Sets background for image label based on dark mode."""
        if dark_mode:
            self.img_label.setStyleSheet("background-color: #1E293B; border-radius: 8px;")
            self.loading_lbl.setStyleSheet("font-weight: bold; color: #38BDF8;")
        else:
            self.img_label.setStyleSheet("background-color: #E2E8F0; border-radius: 8px;")
            self.loading_lbl.setStyleSheet("font-weight: bold; color: #0EA5E9;")

    def start_ocr_process(self, file_path: str):
        """Prepares view and spawns OCR background worker thread."""
        self.file_path = file_path
        self.text_editor.clear()
        
        # Load Document Preview
        self.load_preview(file_path)
        
        # UI controls
        self.loading_widget.show()
        self.btn_analyze.setEnabled(False)
        self.text_editor.setEnabled(False)

        # Start thread
        self.worker = OCRWorker(file_path)
        self.worker.finished.connect(self.on_ocr_finished)
        self.worker.start()

    def on_ocr_finished(self, text: str, error: str):
        """Fires when background OCR task finishes."""
        self.loading_widget.hide()
        self.btn_analyze.setEnabled(True)
        self.text_editor.setEnabled(True)

        if error:
            logger.error(f"OCR failed: {error}")
            self.text_editor.setPlainText(f"OCR Error occurred:\n{error}\n\nPlease enter text manually or retry.")
        else:
            logger.info("OCR completed successfully.")
            self.text_editor.setPlainText(text)

    def load_preview(self, file_path: str):
        """Generates document thumbnail for PDF or loads image directly."""
        _, ext = os.path.splitext(file_path.lower())
        try:
            if ext == ".pdf":
                # Render first page of PDF using PyMuPDF
                doc = fitz.open(file_path)
                if len(doc) > 0:
                    page = doc[0]
                    # Render at slightly lower resolution for thumbnail
                    pix = page.get_pixmap(dpi=100)
                    
                    # Convert to QImage
                    qimg = QImage(pix.samples, pix.width, pix.height, pix.line_bytes, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(qimg)
                    
                    # Scale pixmap
                    scaled = pixmap.scaled(self.img_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.img_label.setPixmap(scaled)
                else:
                    self.img_label.setText("Empty PDF File")
                doc.close()
            else:
                # Load image file directly
                pixmap = QPixmap(file_path)
                scaled = pixmap.scaled(self.img_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.img_label.setPixmap(scaled)
        except Exception as e:
            logger.error(f"Failed to load preview for {file_path}: {e}")
            self.img_label.setText(f"Preview Not Available\n({os.path.basename(file_path)})")

    def resizeEvent(self, event):
        """Handles resizing and updates preview sizing dynamically."""
        super().resizeEvent(event)
        if self.file_path:
            self.load_preview(self.file_path)

    def request_analysis(self):
        """Emits raw text for spaCy/Regex parameters extraction."""
        text = self.text_editor.toPlainText().strip()
        if not text:
            # Warn if empty
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Text", "Please provide or verify the extracted text before running analysis.")
            return
        self.analysis_requested.emit(text, self.file_path)
