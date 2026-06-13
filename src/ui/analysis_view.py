from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTableWidget, QTableWidgetItem,
    QPushButton, QTextEdit, QProgressBar, QMessageBox, QFileDialog, QHeaderView
)
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from src.services.analysis_service import AnalysisService
from src.services.ai_service import AIService
from src.services.pdf_export import PDFExportService
from src.ui.styles import Styles
import os
import logging

logger = logging.getLogger("MedicalApp.AnalysisView")

class AIWorker(QThread):
    """Worker thread to generate AI summary without blocking GUI."""
    finished = pyqtSignal(str)

    def __init__(self, ai_service: AIService, parameters: list):
        super().__init__()
        self.ai_service = ai_service
        self.parameters = parameters

    def run(self):
        summary = self.ai_service.generate_summary(self.parameters)
        self.finished.emit(summary)

class AnalysisView(QWidget):
    """Displays parameter classification table and AI-generated clinical summary."""
    
    back_to_upload_requested = pyqtSignal()
    view_history_requested = pyqtSignal()

    def __init__(self, db_manager, ai_service):
        super().__init__()
        self.db = db_manager
        self.ai = ai_service
        
        self.user_id = None
        self.username = ""
        self.email = ""
        
        self.report_id = None
        self.file_path = None
        self.parameters = []
        self.ai_summary = ""
        self.ai_worker = None
        self.dark_mode = False
        
        self.setup_ui()

    def setup_ui(self):
        """Builds parameter table, summary text box, progress indicators, and button controls."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_layout = QVBoxLayout()
        header = QLabel("Analysis Results")
        header.setObjectName("HeaderLabel")
        header_layout.addWidget(header)
        
        self.subheader = QLabel("Lab report parameter classifications and expert AI summary")
        self.subheader.setObjectName("SubHeaderLabel")
        header_layout.addWidget(self.subheader)
        layout.addLayout(header_layout)

        # 1. Parameters Table Card
        table_card = QFrame()
        table_card.setObjectName("DashboardCard")
        table_layout = QVBoxLayout(table_card)
        table_layout.addWidget(QLabel("Biometric Values & Classification", objectName="CardTitle"))

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Parameter", "Value", "Unit", "Status", "Clinical Reference Range"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setAlternatingRowColors(True)
        table_layout.addWidget(self.table)
        
        layout.addWidget(table_card, stretch=2)

        # 2. AI Summary Card
        summary_card = QFrame()
        summary_card.setObjectName("DashboardCard")
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.addWidget(QLabel("AI-Generated Clinical Summary", objectName="CardTitle"))

        # AI loading progress
        self.ai_progress = QProgressBar()
        self.ai_progress.setRange(0, 0)
        self.ai_progress.setFixedHeight(6)
        self.ai_progress.hide()
        summary_layout.addWidget(self.ai_progress)

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setPlaceholderText("Generating AI Health Summary...")
        summary_layout.addWidget(self.summary_text)

        layout.addWidget(summary_card, stretch=1)

        # 3. Actions Row
        actions_layout = QHBoxLayout()
        self.btn_reupload = QPushButton("Upload New Report")
        self.btn_reupload.setObjectName("SecondaryButton")
        self.btn_reupload.clicked.connect(lambda: self.back_to_upload_requested.emit())
        actions_layout.addWidget(self.btn_reupload)

        self.btn_history = QPushButton("View History Log")
        self.btn_history.setObjectName("SecondaryButton")
        self.btn_history.clicked.connect(lambda: self.view_history_requested.emit())
        actions_layout.addWidget(self.btn_history)
        
        actions_layout.addStretch()

        self.btn_export = QPushButton("📥 Export Report PDF")
        self.btn_export.clicked.connect(self.export_pdf)
        actions_layout.addWidget(self.btn_export)
        
        layout.addLayout(actions_layout)

    def load_results(self, user_id: int, username: str, email: str, report_id: int, file_path: str, parameters: list, dark_mode: bool = False):
        """Populates parameter table, saves data, and fires background AI thread."""
        self.user_id = user_id
        self.username = username
        self.email = email
        
        self.report_id = report_id
        self.file_path = file_path
        self.parameters = parameters
        self.dark_mode = dark_mode
        self.ai_summary = ""
        
        self.summary_text.clear()
        self.summary_text.setPlaceholderText("Generating clinical summary via local Ollama model...")
        self.ai_progress.show()
        self.btn_export.setEnabled(False)

        # Fill Table
        self.table.setRowCount(0)
        for row, p in enumerate(parameters):
            name = p.get("parameter_name", "")
            val = p.get("value", 0.0)
            unit = p.get("unit", "")
            
            # Call Analysis service
            classification, ref_range = AnalysisService.analyze_parameter(name, val)
            p["classification"] = classification
            p["reference_range"] = ref_range
            
            self.table.insertRow(row)
            
            # Name
            self.table.setItem(row, 0, QTableWidgetItem(name))
            
            # Value
            val_item = QTableWidgetItem(f"{val:.2f}" if isinstance(val, float) else str(val))
            val_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row, 1, val_item)
            
            # Unit
            self.table.setItem(row, 2, QTableWidgetItem(unit))
            
            # Status Badge widget
            status_item = QTableWidgetItem(classification)
            status_item.setTextAlignment(Qt.AlignCenter)
            
            # Create a label badge
            badge = QLabel(classification)
            badge.setStyleSheet(Styles.get_badge_style(classification))
            badge.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(row, 3, badge)
            
            # Reference Range
            self.table.setItem(row, 4, QTableWidgetItem(ref_range))

        # Start asynchronous AI worker
        self.ai_worker = AIWorker(self.ai, self.parameters)
        self.ai_worker.finished.connect(self.on_ai_summary_finished)
        self.ai_worker.start()

    def on_ai_summary_finished(self, summary: str):
        """Triggered when the background AI worker returns the health summary."""
        self.ai_progress.hide()
        self.btn_export.setEnabled(True)
        self.ai_summary = summary
        self.summary_text.setPlainText(summary)

    def export_pdf(self):
        """Opens file dialog and triggers ReportLab PDF generator."""
        if not self.parameters:
            QMessageBox.warning(self, "No Data", "No parameter data to export.")
            return

        default_name = f"Aura_Report_{os.path.basename(self.file_path).split('.')[0]}.pdf"
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report",
            default_name,
            "PDF Files (*.pdf)"
        )
        
        if output_path:
            success = PDFExportService.export_report_to_pdf(
                output_path=output_path,
                patient_name=self.username.capitalize(),
                email=self.email,
                report_date=os.path.basename(self.file_path),  # Using path/file as reference
                parameters=self.parameters,
                ai_summary=self.ai_summary
            )
            if success:
                # Log action to history
                self.db.add_history_entry(self.user_id, self.report_id, "Exported PDF")
                QMessageBox.information(self, "Success", f"Report successfully saved to:\n{output_path}")
            else:
                QMessageBox.critical(self, "Export Failed", "Could not generate PDF report. Check logs.")
