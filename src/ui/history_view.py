from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit, QComboBox,
    QDateEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog
)
from PyQt5.QtCore import pyqtSignal, Qt, QDate
from datetime import datetime
import os
import logging
from src.services.pdf_export import PDFExportService
from src.services.ai_service import AIService

logger = logging.getLogger("MedicalApp.HistoryView")

class HistoryView(QWidget):
    """View to search, filter, delete, and view previous clinical reports."""
    
    # Emits report_id, file_path, parameters
    view_details_requested = pyqtSignal(int, str, list)

    def __init__(self, db_manager, ai_service):
        super().__init__()
        self.db = db_manager
        self.ai = ai_service
        self.user_id = None
        self.username = ""
        self.email = ""
        self.dark_mode = False
        
        self.setup_ui()

    def setup_ui(self):
        """Creates search bars, filter selections, history data table, and action hookups."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_layout = QVBoxLayout()
        header = QLabel("Report History")
        header.setObjectName("HeaderLabel")
        header_layout.addWidget(header)
        
        subheader = QLabel("Search and review historical lab report analyses")
        subheader.setObjectName("SubHeaderLabel")
        header_layout.addWidget(subheader)
        layout.addLayout(header_layout)

        # 1. Search & Filter Bar Card
        filter_card = QFrame()
        filter_card.setObjectName("DashboardCard")
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setSpacing(10)

        # Search Query
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by filename or parameter...")
        self.search_input.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_input, stretch=2)

        # Status Dropdown
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All Classifications", "Normal", "Low", "High", "Critical"])
        self.status_combo.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.status_combo, stretch=1)

        # Date Pickers
        filter_layout.addWidget(QLabel("From:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        # Default to 6 months ago
        self.start_date.setDate(QDate.currentDate().addMonths(-6))
        self.start_date.dateChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.start_date)

        filter_layout.addWidget(QLabel("To:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.dateChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.end_date)

        # Reset button
        btn_reset = QPushButton("Reset Filters")
        btn_reset.setObjectName("SecondaryButton")
        btn_reset.clicked.connect(self.reset_filters)
        filter_layout.addWidget(btn_reset)

        layout.addWidget(filter_card)

        # 2. History Table Card
        table_card = QFrame()
        table_card.setObjectName("DashboardCard")
        table_layout = QVBoxLayout(table_card)
        table_layout.addWidget(QLabel("All Analyzed Reports", objectName="CardTitle"))

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Upload Date", "File Name", "Type", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Give actions column slightly more room
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setAlternatingRowColors(True)
        table_layout.addWidget(self.table)

        layout.addWidget(table_card, stretch=1)

    def refresh(self, user_id: int, username: str, email: str, dark_mode: bool = False):
        """Loads and updates history parameters."""
        self.user_id = user_id
        self.username = username
        self.email = email
        self.dark_mode = dark_mode
        self.apply_filters()

    def reset_filters(self):
        """Clears input criteria fields."""
        self.search_input.clear()
        self.status_combo.setCurrentIndex(0)
        self.start_date.setDate(QDate.currentDate().addMonths(-6))
        self.end_date.setDate(QDate.currentDate())
        self.apply_filters()

    def apply_filters(self):
        """Queries database based on filter states and builds the UI rows."""
        if self.user_id is None:
            return

        search = self.search_input.text().strip()
        status = self.status_combo.currentText()
        if status == "All Classifications":
            status = None
            
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")

        reports = self.db.query_history(
            user_id=self.user_id,
            search_query=search,
            filter_status=status,
            start_date=start,
            end_date=end
        )

        self.table.setRowCount(0)
        for row, rep in enumerate(reports):
            report_id = rep["report_id"]
            file_path = rep["file_path"]
            upload_date = rep["upload_date"]
            file_type = rep["file_type"]

            # Parse upload date for nice presentation
            try:
                dt = datetime.strptime(upload_date, "%Y-%m-%d %H:%M:%S")
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except ValueError:
                date_str = upload_date

            self.table.insertRow(row)
            
            # Col 0: Upload Date
            self.table.setItem(row, 0, QTableWidgetItem(date_str))
            
            # Col 1: Filename
            file_name = os.path.basename(file_path)
            self.table.setItem(row, 1, QTableWidgetItem(file_name))
            
            # Col 2: File Type
            self.table.setItem(row, 2, QTableWidgetItem(file_type.upper()))

            # Col 3: Actions Container Layout
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            actions_layout.setSpacing(6)

            # View Button
            btn_view = QPushButton("👁 View")
            btn_view.clicked.connect(lambda checked, r_id=report_id, path=file_path: self.view_report(r_id, path))
            btn_view.setFixedWidth(65)
            btn_view.setStyleSheet("font-size: 11px; padding: 4px;")
            actions_layout.addWidget(btn_view)

            # PDF Export Button
            btn_pdf = QPushButton("PDF")
            btn_pdf.setObjectName("SecondaryButton")
            btn_pdf.clicked.connect(lambda checked, r_id=report_id, path=file_path: self.export_pdf(r_id, path))
            btn_pdf.setFixedWidth(55)
            btn_pdf.setStyleSheet("font-size: 11px; padding: 4px;")
            actions_layout.addWidget(btn_pdf)

            # Delete Button
            btn_del = QPushButton("Delete")
            btn_del.setObjectName("DeleteButton")
            btn_del.clicked.connect(lambda checked, r_id=report_id: self.delete_report(r_id))
            btn_del.setFixedWidth(60)
            btn_del.setStyleSheet("font-size: 11px; padding: 4px;")
            actions_layout.addWidget(btn_del)

            self.table.setCellWidget(row, 3, actions_widget)

    def view_report(self, report_id: int, file_path: str):
        """Fetches parameters for the selected report from the DB and emits details."""
        logger.info(f"Loading history report ID: {report_id}")
        db_rows = self.db.get_report_analysis_details(report_id)
        
        # Convert DB rows back to standard list of dicts
        parameters = []
        for r in db_rows:
            parameters.append({
                "parameter_name": r["parameter_name"],
                "value": r["value"],
                "unit": r["unit"],
                "classification": r["classification"],
                "reference_range": r["reference_range"]
            })
            
        self.view_details_requested.emit(report_id, file_path, parameters)

    def export_pdf(self, report_id: int, file_path: str):
        """Generates and downloads the PDF directly from history record data."""
        db_rows = self.db.get_report_analysis_details(report_id)
        if not db_rows:
            QMessageBox.warning(self, "No Data", "No report details found in database.")
            return

        parameters = []
        for r in db_rows:
            parameters.append({
                "parameter_name": r["parameter_name"],
                "value": r["value"],
                "unit": r["unit"],
                "classification": r["classification"],
                "reference_range": r["reference_range"]
            })

        # Generate summary
        ai_summary = self.ai.generate_summary(parameters)

        default_name = f"Aura_History_Report_{os.path.basename(file_path).split('.')[0]}.pdf"
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
                report_date=os.path.basename(file_path),
                parameters=parameters,
                ai_summary=ai_summary
            )
            if success:
                self.db.add_history_entry(self.user_id, report_id, "Exported PDF")
                QMessageBox.information(self, "Success", f"Report saved: {output_path}")
            else:
                QMessageBox.critical(self, "Export Failed", "Could not save PDF.")

    def delete_report(self, report_id: int):
        """Prompts confirmation and removes database reference."""
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this report? This will permanently erase the report record and all its analyzed parameters.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            success = self.db.delete_report(report_id, self.user_id)
            if success:
                logger.info(f"Report ID {report_id} successfully deleted.")
                self.apply_filters()
            else:
                QMessageBox.critical(self, "Error", "Could not delete report.")
