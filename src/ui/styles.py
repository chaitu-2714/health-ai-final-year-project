class Styles:
    """Contains stylesheets and visual design parameters for the application."""
    
    @staticmethod
    def get_stylesheet(dark_mode: bool = False) -> str:
        """Returns the QSS stylesheet for the application based on the mode."""
        if dark_mode:
            return Styles._dark_stylesheet()
        else:
            return Styles._light_stylesheet()

    @staticmethod
    def _light_stylesheet() -> str:
        return """
            /* General styling */
            QWidget {
                background-color: #F8FAFC;
                color: #0F172A;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            
            /* Sidebar layout */
            #SidebarFrame {
                background-color: #0F172A;
                border-right: 1px solid #E2E8F0;
                min-width: 230px;
                max-width: 230px;
            }
            
            #SidebarFrame QLabel {
                color: #FFFFFF;
                background-color: transparent;
            }
            
            #SidebarButton {
                background-color: transparent;
                color: #94A3B8;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                text-align: left;
                font-weight: bold;
                font-size: 13px;
            }
            
            #SidebarButton:hover {
                background-color: #1E293B;
                color: #F8FAFC;
            }
            
            #SidebarButton[active="true"] {
                background-color: #0EA5E9;
                color: #FFFFFF;
            }
            
            /* Content Area */
            #HeaderLabel {
                font-size: 22px;
                font-weight: bold;
                color: #0F172A;
                background-color: transparent;
                border: none;
            }

            #SubHeaderLabel {
                font-size: 13px;
                color: #64748B;
                background-color: transparent;
            }
            
            /* Cards */
            #DashboardCard {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                padding: 15px;
            }
            
            #DashboardCard QLabel {
                background-color: transparent;
            }
            
            #CardTitle {
                font-size: 13px;
                color: #64748B;
                font-weight: bold;
            }
            
            #CardValue {
                font-size: 26px;
                font-weight: bold;
                color: #0F172A;
            }
            
            /* Forms and Inputs */
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 8px 12px;
                color: #0F172A;
            }
            
            QLineEdit:focus {
                border: 2px solid #38BDF8;
                background-color: #FFFFFF;
            }
            
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 8px;
                color: #0F172A;
            }
            
            QTextEdit:focus {
                border: 2px solid #38BDF8;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #0284C7;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #0369A1;
            }
            
            QPushButton:pressed {
                background-color: #075985;
            }
            
            QPushButton#SecondaryButton {
                background-color: #E2E8F0;
                color: #334155;
            }
            
            QPushButton#SecondaryButton:hover {
                background-color: #CBD5E1;
            }
            
            QPushButton#DeleteButton {
                background-color: #EF4444;
                color: #FFFFFF;
            }
            
            QPushButton#DeleteButton:hover {
                background-color: #DC2626;
            }
            
            /* Table view */
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                gridline-color: #F1F5F9;
            }
            
            QHeaderView::section {
                background-color: #F1F5F9;
                color: #475569;
                padding: 8px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #E2E8F0;
            }
            
            /* Labels */
            QLabel#TitleLabel {
                font-size: 28px;
                font-weight: bold;
                color: #0284C7;
                background-color: transparent;
            }
            
            /* ScrollBars */
            QScrollBar:vertical {
                border: none;
                background: #F1F5F9;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }
        """

    @staticmethod
    def _dark_stylesheet() -> str:
        return """
            /* General styling */
            QWidget {
                background-color: #0F172A;
                color: #F8FAFC;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            
            /* Sidebar layout */
            #SidebarFrame {
                background-color: #020617;
                border-right: 1px solid #1E293B;
                min-width: 230px;
                max-width: 230px;
            }
            
            #SidebarFrame QLabel {
                color: #FFFFFF;
                background-color: transparent;
            }
            
            #SidebarButton {
                background-color: transparent;
                color: #64748B;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                text-align: left;
                font-weight: bold;
                font-size: 13px;
            }
            
            #SidebarButton:hover {
                background-color: #0F172A;
                color: #F8FAFC;
            }
            
            #SidebarButton[active="true"] {
                background-color: #0EA5E9;
                color: #FFFFFF;
            }
            
            /* Content Area */
            #HeaderLabel {
                font-size: 22px;
                font-weight: bold;
                color: #F8FAFC;
                background-color: transparent;
                border: none;
            }

            #SubHeaderLabel {
                font-size: 13px;
                color: #94A3B8;
                background-color: transparent;
            }
            
            /* Cards */
            #DashboardCard {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 15px;
            }
            
            #DashboardCard QLabel {
                background-color: transparent;
            }
            
            #CardTitle {
                font-size: 13px;
                color: #94A3B8;
                font-weight: bold;
            }
            
            #CardValue {
                font-size: 26px;
                font-weight: bold;
                color: #F8FAFC;
            }
            
            /* Forms and Inputs */
            QLineEdit {
                background-color: #1E293B;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 8px 12px;
                color: #F8FAFC;
            }
            
            QLineEdit:focus {
                border: 2px solid #0EA5E9;
                background-color: #1E293B;
            }
            
            QTextEdit {
                background-color: #1E293B;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 8px;
                color: #F8FAFC;
            }
            
            QTextEdit:focus {
                border: 2px solid #0EA5E9;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #0EA5E9;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #0284C7;
            }
            
            QPushButton:pressed {
                background-color: #0369A1;
            }
            
            QPushButton#SecondaryButton {
                background-color: #334155;
                color: #E2E8F0;
            }
            
            QPushButton#SecondaryButton:hover {
                background-color: #475569;
            }
            
            QPushButton#DeleteButton {
                background-color: #EF4444;
                color: #FFFFFF;
            }
            
            QPushButton#DeleteButton:hover {
                background-color: #DC2626;
            }
            
            /* Table view */
            QTableWidget {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 8px;
                gridline-color: #334155;
            }
            
            QHeaderView::section {
                background-color: #0F172A;
                color: #94A3B8;
                padding: 8px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #334155;
            }
            
            /* Labels */
            QLabel#TitleLabel {
                font-size: 28px;
                font-weight: bold;
                color: #0EA5E9;
                background-color: transparent;
            }
            
            /* ScrollBars */
            QScrollBar:vertical {
                border: none;
                background: #1E293B;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #475569;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #64748B;
            }
        """
        
    @staticmethod
    def get_badge_style(classification: str) -> str:
        """Returns inline styles for color-coded status badges."""
        styles = {
            "Normal": "color: #FFFFFF; background-color: #10B981; border-radius: 4px; padding: 2px 6px; font-weight: bold;",
            "Low": "color: #0F172A; background-color: #F59E0B; border-radius: 4px; padding: 2px 6px; font-weight: bold;",
            "High": "color: #FFFFFF; background-color: #F97316; border-radius: 4px; padding: 2px 6px; font-weight: bold;",
            "Critical": "color: #FFFFFF; background-color: #EF4444; border-radius: 4px; padding: 2px 6px; font-weight: bold;"
        }
        return styles.get(classification, "color: #FFFFFF; background-color: #64748B; border-radius: 4px; padding: 2px 6px;")
