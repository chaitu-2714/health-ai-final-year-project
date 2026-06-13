from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime
import logging

logger = logging.getLogger("MedicalApp.DashboardView")

class MplCanvas(FigureCanvas):
    """A canvas for rendering Matplotlib plots inside the PyQt5 application."""
    
    def __init__(self, width=5, height=3, dpi=100, dark_mode=False):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.dark_mode = dark_mode
        self.apply_theme()
        super().__init__(self.fig)

    def apply_theme(self):
        """Customizes chart colors and styles matching light/dark mode."""
        if self.dark_mode:
            self.fig.patch.set_facecolor('#1E293B')
            self.axes.set_facecolor('#0F172A')
            self.axes.spines['bottom'].set_color('#475569')
            self.axes.spines['top'].set_color('#475569')
            self.axes.spines['left'].set_color('#475569')
            self.axes.spines['right'].set_color('#475569')
            self.axes.tick_params(colors='#94A3B8', labelsize=9)
            self.axes.yaxis.label.set_color('#94A3B8')
            self.axes.xaxis.label.set_color('#94A3B8')
            self.axes.title.set_color('#F8FAFC')
            self.grid_color = '#334155'
        else:
            self.fig.patch.set_facecolor('#FFFFFF')
            self.axes.set_facecolor('#F8FAFC')
            self.axes.spines['bottom'].set_color('#E2E8F0')
            self.axes.spines['top'].set_color('#E2E8F0')
            self.axes.spines['left'].set_color('#E2E8F0')
            self.axes.spines['right'].set_color('#E2E8F0')
            self.axes.tick_params(colors='#475569', labelsize=9)
            self.axes.yaxis.label.set_color('#475569')
            self.axes.xaxis.label.set_color('#475569')
            self.axes.title.set_color('#0F172A')
            self.grid_color = '#E2E8F0'

class DashboardView(QWidget):
    """Displays user health statistics, parameter charts, and recent reports."""

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.user_id = None
        self.dark_mode = False
        self.setup_ui()

    def setup_ui(self):
        """Creates layout and initializes widgets."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 1. Header Section
        header_layout = QVBoxLayout()
        header = QLabel("Dashboard")
        header.setObjectName("HeaderLabel")
        header_layout.addWidget(header)
        
        subheader = QLabel("Overview of your biometric metrics and health trends")
        subheader.setObjectName("SubHeaderLabel")
        header_layout.addWidget(subheader)
        layout.addLayout(header_layout)
        
        # 2. Stat Cards Grid (Total Uploads, Health Score, Alerts)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.card_uploads = self.create_stat_card("Total Reports Uploaded", "0")
        self.card_score = self.create_stat_card("Current Health Score", "100")
        self.card_alerts = self.create_stat_card("Critical Alerts Found", "0")
        
        stats_layout.addWidget(self.card_uploads)
        stats_layout.addWidget(self.card_score)
        stats_layout.addWidget(self.card_alerts)
        layout.addLayout(stats_layout)
        
        # 3. Middle Section: Trend Charts & Recent Uploads
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(15)
        
        # Left Panel - Charts Layout
        charts_panel = QFrame()
        charts_panel.setObjectName("DashboardCard")
        charts_panel_layout = QVBoxLayout(charts_panel)
        charts_panel_layout.addWidget(QLabel("Historical Parameter Trends", objectName="CardTitle"))
        
        charts_grid = QGridLayout()
        self.canvas_hgb = MplCanvas(width=4, height=2.2, dark_mode=self.dark_mode)
        self.canvas_glucose = MplCanvas(width=4, height=2.2, dark_mode=self.dark_mode)
        self.canvas_bp = MplCanvas(width=4, height=2.2, dark_mode=self.dark_mode)
        charts_grid.addWidget(self.canvas_hgb, 0, 0)
        charts_grid.addWidget(self.canvas_glucose, 0, 1)
        charts_grid.addWidget(self.canvas_bp, 1, 0, 1, 2)  # Spans across both columns in row 1
        charts_panel_layout.addLayout(charts_grid)
        middle_layout.addWidget(charts_panel, stretch=2)
        
        # Right Panel - Recent Activity
        recent_panel = QFrame()
        recent_panel.setObjectName("DashboardCard")
        recent_panel.setFixedWidth(260)
        recent_layout = QVBoxLayout(recent_panel)
        
        recent_title = QLabel("Recent Uploads")
        recent_title.setObjectName("CardTitle")
        recent_layout.addWidget(recent_title)
        
        self.recent_list = QListWidget()
        self.recent_list.setStyleSheet("border: none; background: transparent;")
        recent_layout.addWidget(self.recent_list)
        
        middle_layout.addWidget(recent_panel, stretch=1)
        layout.addLayout(middle_layout)

    def create_stat_card(self, title: str, value: str) -> QFrame:
        """Helper to create standard rounded stat card layout."""
        card = QFrame()
        card.setObjectName("DashboardCard")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(5)
        
        lbl_title = QLabel(title)
        lbl_title.setObjectName("CardTitle")
        card_layout.addWidget(lbl_title)
        
        lbl_value = QLabel(value)
        lbl_value.setObjectName("CardValue")
        lbl_value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        card_layout.addWidget(lbl_value)
        
        return card

    def refresh(self, user_id: int, dark_mode: bool = False):
        """Loads data from SQLite database and updates all views."""
        self.user_id = user_id
        self.dark_mode = dark_mode
        
        # Propagate theme changes to canvases
        self.canvas_hgb.dark_mode = dark_mode
        self.canvas_hgb.apply_theme()
        self.canvas_glucose.dark_mode = dark_mode
        self.canvas_glucose.apply_theme()
        self.canvas_bp.dark_mode = dark_mode
        self.canvas_bp.apply_theme()
        
        # Query metrics
        stats = self.db.get_dashboard_summary(user_id)
        self.card_uploads.findChild(QLabel, "CardValue").setText(str(stats["total_reports"]))
        self.card_score.findChild(QLabel, "CardValue").setText(f"{stats['health_score']}/100")
        
        # Apply conditional coloring on Alerts
        alerts_lbl = self.card_alerts.findChild(QLabel, "CardValue")
        alerts_lbl.setText(str(stats["critical_parameters"]))
        if stats["critical_parameters"] > 0:
            alerts_lbl.setStyleSheet("color: #EF4444; font-weight: bold;")
        else:
            alerts_lbl.setStyleSheet("color: #10B981;" if not dark_mode else "color: #34D399;")
            
        # Refresh Recent list
        self.recent_list.clear()
        reports = self.db.get_user_reports(user_id)[:5]
        for rep in reports:
            file_name = os.path.basename(rep["file_path"])
            dt = datetime.strptime(rep["upload_date"], "%Y-%m-%d %H:%M:%S")
            date_str = dt.strftime("%b %d, %H:%M")
            item = QListWidgetItem(f"📄 {file_name}\n   {date_str}")
            self.recent_list.addItem(item)
            
        # Draw Charts
        self.plot_parameter_chart(self.canvas_hgb, "Hemoglobin", "Hemoglobin Levels Over Time", "g/dL", "#0EA5E9")
        self.plot_parameter_chart(self.canvas_glucose, "Blood Sugar", "Fasting Glucose Over Time", "mg/dL", "#EF4444")
        self.plot_blood_pressure_chart(self.canvas_bp)

    def plot_parameter_chart(self, canvas: MplCanvas, param_name: str, title: str, unit: str, color: str):
        """Queries and renders a trend plot on the specified canvas."""
        canvas.axes.clear()
        canvas.apply_theme()  # Re-apply color palette settings
        
        trends = self.db.get_parameter_trends(self.user_id, param_name)
        
        if not trends:
            # Show empty grid placeholder message
            canvas.axes.text(0.5, 0.5, f"No historical {param_name} data.\nUpload reports to track trends.", 
                             horizontalalignment='center', verticalalignment='center',
                             transform=canvas.axes.transAxes, color='#94A3B8' if self.dark_mode else '#64748B')
            canvas.axes.set_title(title, pad=10)
            canvas.axes.grid(True, linestyle='--', alpha=0.3, color=canvas.grid_color)
            canvas.draw()
            return

        # Parse date and values
        dates = []
        values = []
        for val, date_str in trends:
            try:
                # SQLite timestamp parsing
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                dates.append(dt)
                values.append(val)
            except ValueError:
                continue

        # Plot line
        canvas.axes.plot(dates, values, marker='o', color=color, linewidth=2, markersize=5)
        canvas.axes.set_title(title, pad=10)
        canvas.axes.set_ylabel(f"Value ({unit})")
        canvas.axes.grid(True, linestyle='--', alpha=0.3, color=canvas.grid_color)
        
        # X-Axis formatting
        canvas.axes.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        canvas.axes.xaxis.set_major_locator(mdates.AutoDateLocator())
        canvas.fig.autofmt_xdate(bottom=0.2, rotation=30)
        
        canvas.draw()

    def plot_blood_pressure_chart(self, canvas: MplCanvas):
        """Queries and renders dual Systolic and Diastolic trend lines on the same canvas."""
        canvas.axes.clear()
        canvas.apply_theme()
        
        systolic_trends = self.db.get_parameter_trends(self.user_id, "Systolic Blood Pressure")
        diastolic_trends = self.db.get_parameter_trends(self.user_id, "Diastolic Blood Pressure")
        
        if not systolic_trends or not diastolic_trends:
            canvas.axes.text(0.5, 0.5, "No historical Blood Pressure data.\nUpload reports to track trends.", 
                             horizontalalignment='center', verticalalignment='center',
                             transform=canvas.axes.transAxes, color='#94A3B8' if self.dark_mode else '#64748B')
            canvas.axes.set_title("Blood Pressure Trends Over Time", pad=10)
            canvas.axes.grid(True, linestyle='--', alpha=0.3, color=canvas.grid_color)
            canvas.draw()
            return

        # Parse Systolic
        sys_dates = []
        sys_vals = []
        for val, date_str in systolic_trends:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                sys_dates.append(dt)
                sys_vals.append(val)
            except ValueError:
                continue

        # Parse Diastolic
        dia_dates = []
        dia_vals = []
        for val, date_str in diastolic_trends:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                dia_dates.append(dt)
                dia_vals.append(val)
            except ValueError:
                continue

        # Plot lines
        canvas.axes.plot(sys_dates, sys_vals, marker='o', color="#F97316", linewidth=2, label="Systolic")
        canvas.axes.plot(dia_dates, dia_vals, marker='s', color="#0EA5E9", linewidth=2, label="Diastolic")
        
        canvas.axes.set_title("Blood Pressure Trends (Systolic / Diastolic)", pad=10)
        canvas.axes.set_ylabel("Value (mmHg)")
        canvas.axes.grid(True, linestyle='--', alpha=0.3, color=canvas.grid_color)
        canvas.axes.legend(loc="upper left", framealpha=0.4)
        
        # X-Axis formatting
        canvas.axes.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        canvas.axes.xaxis.set_major_locator(mdates.AutoDateLocator())
        canvas.fig.autofmt_xdate(bottom=0.2, rotation=30)
        
        canvas.draw()
