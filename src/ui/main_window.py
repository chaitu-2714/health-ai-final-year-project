from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton, QStackedWidget
)
from PyQt5.QtCore import Qt
from src.ui.styles import Styles
from src.ui.auth_view import AuthView
from src.ui.dashboard_view import DashboardView
from src.ui.upload_view import UploadView
from src.ui.ocr_view import OCRView
from src.ui.analysis_view import AnalysisView
from src.ui.history_view import HistoryView
from src.ui.settings_view import SettingsView
from src.services.analysis_service import AnalysisService
from src.services.extraction_service import ExtractionService
from src.services.ai_service import AIService
import logging

logger = logging.getLogger("MedicalApp.MainWindow")

class MainWindow(QMainWindow):
    """Main window shell managing sidebar navigation, dark/light theme, and view routing."""

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        
        # Initialize Services
        self.extractor = ExtractionService()
        self.ai_service = AIService()  # Default local URL and model
        
        # State Variables
        self.user_id = None
        self.username = ""
        self.email = ""
        
        # Load config to set initial theme
        try:
            from src.utils import get_config
            config = get_config()
            self.dark_mode = config.get("dark_mode", False)
        except Exception:
            self.dark_mode = False
        
        self.setWindowTitle("Aura AI - Medical Report Analysis")
        self.resize(1100, 750)
        self.setMinimumSize(950, 650)
        
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Creates left sidebar layout and stacks all sub-widget views."""
        # Main Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Left Sidebar Panel
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("SidebarFrame")
        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(15, 25, 15, 25)
        sidebar_layout.setSpacing(15)

        # Brand Title
        brand_lbl = QLabel("Aura Health")
        brand_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #38BDF8; margin-bottom: 20px;")
        brand_lbl.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(brand_lbl)

        # Profile Card
        self.profile_card = QFrame()
        self.profile_card.setStyleSheet("background-color: #1E293B; border-radius: 8px; padding: 10px;")
        self.profile_card.setFixedHeight(75)
        profile_layout = QVBoxLayout(self.profile_card)
        profile_layout.setContentsMargins(8, 8, 8, 8)
        profile_layout.setSpacing(2)
        
        self.lbl_profile_name = QLabel("John Doe")
        self.lbl_profile_name.setStyleSheet("font-weight: bold; font-size: 13px; color: #F8FAFC;")
        self.lbl_profile_email = QLabel("john@gmail.com")
        self.lbl_profile_email.setStyleSheet("font-size: 11px; color: #94A3B8;")
        
        profile_layout.addWidget(self.lbl_profile_name)
        profile_layout.addWidget(self.lbl_profile_email)
        sidebar_layout.addWidget(self.profile_card)
        sidebar_layout.addSpacing(10)

        # Navigation Buttons
        self.btn_dashboard = QPushButton("📊 Dashboard")
        self.btn_dashboard.setObjectName("SidebarButton")
        self.btn_dashboard.clicked.connect(self.go_to_dashboard)
        sidebar_layout.addWidget(self.btn_dashboard)

        self.btn_upload = QPushButton("📥 Upload Report")
        self.btn_upload.setObjectName("SidebarButton")
        self.btn_upload.clicked.connect(self.go_to_upload)
        sidebar_layout.addWidget(self.btn_upload)

        self.btn_history = QPushButton("📜 Report History")
        self.btn_history.setObjectName("SidebarButton")
        self.btn_history.clicked.connect(self.go_to_history)
        sidebar_layout.addWidget(self.btn_history)

        self.btn_settings = QPushButton("⚙️ Settings")
        self.btn_settings.setObjectName("SidebarButton")
        self.btn_settings.clicked.connect(self.go_to_settings)
        sidebar_layout.addWidget(self.btn_settings)

        sidebar_layout.addStretch()

        # Theme Switcher Button
        self.btn_theme = QPushButton("☀️ Light Mode" if self.dark_mode else "🌙 Dark Mode")
        self.btn_theme.setObjectName("SidebarButton")
        self.btn_theme.setStyleSheet("color: #E2E8F0;")
        self.btn_theme.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.btn_theme)

        # Log Out Button
        self.btn_logout = QPushButton("🚪 Log Out")
        self.btn_logout.setObjectName("SidebarButton")
        self.btn_logout.setStyleSheet("color: #F87171;")
        self.btn_logout.clicked.connect(self.handle_logout)
        sidebar_layout.addWidget(self.btn_logout)

        main_layout.addWidget(self.sidebar_frame)

        # 2. Central Content Stacked Widget
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, stretch=1)

        # Initialize and add all views to Stack
        self.auth_view = AuthView(self.db)
        self.dashboard_view = DashboardView(self.db)
        self.upload_view = UploadView()
        self.ocr_view = OCRView()
        self.analysis_view = AnalysisView(self.db, self.ai_service)
        self.history_view = HistoryView(self.db, self.ai_service)
        self.settings_view = SettingsView()

        self.content_stack.addWidget(self.auth_view)
        self.content_stack.addWidget(self.dashboard_view)
        self.content_stack.addWidget(self.upload_view)
        self.content_stack.addWidget(self.ocr_view)
        self.content_stack.addWidget(self.analysis_view)
        self.content_stack.addWidget(self.history_view)
        self.content_stack.addWidget(self.settings_view)

        # Connect Signals
        self.auth_view.login_successful.connect(self.handle_login_success)
        self.upload_view.file_selected.connect(self.handle_file_uploaded)
        self.ocr_view.btn_back.clicked.connect(self.go_to_upload)
        self.ocr_view.analysis_requested.connect(self.handle_analysis_requested)
        
        self.analysis_view.back_to_upload_requested.connect(self.go_to_upload)
        self.analysis_view.view_history_requested.connect(self.go_to_history)
        
        self.history_view.view_details_requested.connect(self.handle_view_history_details)
        self.settings_view.config_updated.connect(self.handle_config_updated)

        # Initial logged out view state
        self.sidebar_frame.hide()
        self.content_stack.setCurrentWidget(self.auth_view)

    def apply_theme(self):
        """Re-applies the application QSS stylesheet according to dark_mode flag."""
        stylesheet = Styles.get_stylesheet(self.dark_mode)
        self.setStyleSheet(stylesheet)
        
        # Propagate custom settings to child widgets
        self.upload_view.set_theme_colors(self.dark_mode)
        self.ocr_view.set_theme_colors(self.dark_mode)
        
        # Redraw charts if we are on Dashboard
        if self.content_stack.currentWidget() == self.dashboard_view:
            self.dashboard_view.refresh(self.user_id, self.dark_mode)

    def toggle_theme(self):
        """Inverts the theme flag and re-evaluates stylesheets."""
        self.dark_mode = not self.dark_mode
        self.btn_theme.setText("☀️ Light Mode" if self.dark_mode else "🌙 Dark Mode")
        
        # Save preference to config
        try:
            from src.utils import get_config, save_config
            config = get_config()
            config["dark_mode"] = self.dark_mode
            save_config(config)
        except Exception as e:
            logger.error(f"Failed to save dark mode setting: {e}")
            
        self.apply_theme()
        logger.info(f"Theme toggled. Dark mode = {self.dark_mode}")

    # --- Authentication handlers ---

    def handle_login_success(self, user_id: int, username: str, email: str):
        """Displays user session panel and redirects to dashboard."""
        self.user_id = user_id
        self.username = username
        self.email = email
        
        # Update Profile Card
        self.lbl_profile_name.setText(username.capitalize())
        self.lbl_profile_email.setText(email)
        
        # Update and show sidebar
        self.sidebar_frame.show()
        self.go_to_dashboard()

    def handle_logout(self):
        """Clears user session data and switches back to credentials screen."""
        self.user_id = None
        self.username = ""
        self.email = ""
        
        self.sidebar_frame.hide()
        self.content_stack.setCurrentWidget(self.auth_view)
        logger.info("User logged out.")

    # --- Navigation View Switchers ---

    def update_sidebar_selection(self, active_button):
        """Sets styling attribute on the sidebar buttons to highlight selected view."""
        buttons = [self.btn_dashboard, self.btn_upload, self.btn_history, self.btn_settings]
        for btn in buttons:
            btn.setProperty("active", "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            
        if active_button:
            active_button.setProperty("active", "true")
            active_button.style().unpolish(active_button)
            active_button.style().polish(active_button)

    def go_to_dashboard(self):
        """Loads metrics and shows dashboard view."""
        self.update_sidebar_selection(self.btn_dashboard)
        self.content_stack.setCurrentWidget(self.dashboard_view)
        self.dashboard_view.refresh(self.user_id, self.dark_mode)

    def go_to_upload(self):
        """Shows report upload view."""
        self.update_sidebar_selection(self.btn_upload)
        self.content_stack.setCurrentWidget(self.upload_view)

    def go_to_history(self):
        """Refreshes parameters and shows history view."""
        self.update_sidebar_selection(self.btn_history)
        self.content_stack.setCurrentWidget(self.history_view)
        self.history_view.refresh(self.user_id, self.username, self.email, self.dark_mode)

    def go_to_settings(self):
        """Shows application configurations view."""
        self.update_sidebar_selection(self.btn_settings)
        self.content_stack.setCurrentWidget(self.settings_view)
        self.settings_view.load_values()

    def handle_config_updated(self):
        """Reloads configuration values (like dark_mode) across views."""
        try:
            from src.utils import get_config
            config = get_config()
            dark = config.get("dark_mode", self.dark_mode)
            if dark != self.dark_mode:
                self.dark_mode = dark
                self.btn_theme.setText("☀️ Light Mode" if self.dark_mode else "🌙 Dark Mode")
                self.apply_theme()
        except Exception as e:
            logger.error(f"Error handling config update: {e}")

    # --- Processing Handlers ---

    def handle_file_uploaded(self, file_path: str):
        """Switches to OCR processing screen and fires extraction worker thread."""
        self.update_sidebar_selection(self.btn_upload)
        self.content_stack.setCurrentWidget(self.ocr_view)
        self.ocr_view.start_ocr_process(file_path)

    def handle_analysis_requested(self, raw_text: str, file_path: str):
        """Performs spaCy/regex parsing, range mapping, database archiving, and loads analysis view."""
        # 1. Extract Parameters
        parameters = self.extractor.extract_parameters(raw_text)
        
        # 2. Check: If no parameters detected, notify user but proceed
        if not parameters:
            # Add a message to let the user know we didn't parse any known fields
            logger.warning("No standard parameters were successfully extracted from the text.")
            
        # 3. Store Report in Database
        # Detect file extension type
        _, ext = os.path.splitext(file_path.lower())
        file_type = ext.replace(".", "")
        
        # Add entry to Reports
        report_id = self.db.add_report(self.user_id, file_path, file_type)
        
        if report_id == -1:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Database Error", "Failed to register report in the database.")
            return

        # 4. Store ExtractedParameters and AnalysisResults in Database
        for p in parameters:
            p_name = p["parameter_name"]
            p_val = p["value"]
            p_unit = p["unit"]
            
            # Save Parameter
            param_id = self.db.add_extracted_parameter(report_id, p_name, p_val, p_unit)
            
            if param_id != -1:
                # Classify parameter to save classification result
                classification, ref_range = AnalysisService.analyze_parameter(p_name, p_val)
                self.db.add_analysis_result(report_id, param_id, classification, ref_range)

        logger.info(f"Report ID {report_id} and parameters successfully archived.")

        # 5. Load Results inside AnalysisView
        self.content_stack.setCurrentWidget(self.analysis_view)
        self.analysis_view.load_results(
            user_id=self.user_id,
            username=self.username,
            email=self.email,
            report_id=report_id,
            file_path=file_path,
            parameters=parameters,
            dark_mode=self.dark_mode
        )

    def handle_view_history_details(self, report_id: int, file_path: str, parameters: list):
        """Displays detail breakdown from history logs directly (re-use analysis view layout)."""
        self.update_sidebar_selection(self.btn_history)
        self.content_stack.setCurrentWidget(self.analysis_view)
        self.analysis_view.load_results(
            user_id=self.user_id,
            username=self.username,
            email=self.email,
            report_id=report_id,
            file_path=file_path,
            parameters=parameters,
            dark_mode=self.dark_mode
        )
