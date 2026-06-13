import sys
import os
import logging

# Ensure root directory is on PATH for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from src.utils.logger import setup_logger
from src.database.db_manager import DBManager
from src.ui.main_window import MainWindow

def main():
    # 1. Setup Logging
    logger = setup_logger(logging.INFO)
    logger.info("Starting Aura Health Application...")

    # 2. Initialize Database
    try:
        db_manager = DBManager()
    except Exception as e:
        logger.critical(f"Failed to initialize database: {e}")
        sys.exit(1)

    # 3. Launch PyQt5 Application
    app = QApplication(sys.argv)
    app.setApplicationName("Aura AI - Medical Report Analysis")
    
    # 4. Initialize Main Window
    window = MainWindow(db_manager)
    window.show()

    logger.info("Aura Application main window displayed. Starting event loop.")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
