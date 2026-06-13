from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox, QStackedWidget
)
from PyQt5.QtCore import pyqtSignal, Qt
from src.utils.helpers import (
    validate_email, validate_username, check_password_strength, hash_password, verify_password
)
import logging

logger = logging.getLogger("MedicalApp.AuthView")

class AuthView(QStackedWidget):
    """Contains the Login and Registration screens, emitting a signal on successful login."""
    
    # Emits user_id, username, email
    login_successful = pyqtSignal(int, str, str)

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        
        # Create views
        self.login_widget = QWidget()
        self.register_widget = QWidget()
        
        self.setup_login_ui()
        self.setup_register_ui()
        
        self.addWidget(self.login_widget)
        self.addWidget(self.register_widget)
        self.setCurrentWidget(self.login_widget)

    def setup_login_ui(self):
        """Sets up the login interface form."""
        layout = QVBoxLayout(self.login_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        # Container Card
        card = QFrame()
        card.setObjectName("DashboardCard")
        card.setFixedWidth(380)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 40, 30, 40)
        card_layout.setSpacing(15)
        
        # Title
        title = QLabel("Aura Health")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)
        
        subtitle = QLabel("Please log in to your account")
        subtitle.setObjectName("SubHeaderLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(15)
        
        # Inputs
        self.login_user_input = QLineEdit()
        self.login_user_input.setPlaceholderText("Username")
        card_layout.addWidget(self.login_user_input)
        
        self.login_pass_input = QLineEdit()
        self.login_pass_input.setPlaceholderText("Password")
        self.login_pass_input.setEchoMode(QLineEdit.Password)
        card_layout.addWidget(self.login_pass_input)
        card_layout.addSpacing(10)
        
        # Action Buttons
        btn_login = QPushButton("Log In")
        btn_login.clicked.connect(self.handle_login)
        card_layout.addWidget(btn_login)
        
        btn_goto_register = QPushButton("Create an Account")
        btn_goto_register.setObjectName("SecondaryButton")
        btn_goto_register.clicked.connect(lambda: self.setCurrentWidget(self.register_widget))
        card_layout.addWidget(btn_goto_register)
        
        layout.addWidget(card)

    def setup_register_ui(self):
        """Sets up the user registration interface form."""
        layout = QVBoxLayout(self.register_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        # Container Card
        card = QFrame()
        card.setObjectName("DashboardCard")
        card.setFixedWidth(380)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(12)
        
        # Title
        title = QLabel("Create Account")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)
        
        subtitle = QLabel("Join Aura Health System")
        subtitle.setObjectName("SubHeaderLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(10)
        
        # Inputs
        self.reg_user_input = QLineEdit()
        self.reg_user_input.setPlaceholderText("Username")
        card_layout.addWidget(self.reg_user_input)
        
        self.reg_email_input = QLineEdit()
        self.reg_email_input.setPlaceholderText("Email address")
        card_layout.addWidget(self.reg_email_input)
        
        self.reg_pass_input = QLineEdit()
        self.reg_pass_input.setPlaceholderText("Password")
        self.reg_pass_input.setEchoMode(QLineEdit.Password)
        card_layout.addWidget(self.reg_pass_input)
        
        self.reg_pass_confirm = QLineEdit()
        self.reg_pass_confirm.setPlaceholderText("Confirm Password")
        self.reg_pass_confirm.setEchoMode(QLineEdit.Password)
        card_layout.addWidget(self.reg_pass_confirm)
        card_layout.addSpacing(8)
        
        # Action Buttons
        btn_register = QPushButton("Register")
        btn_register.clicked.connect(self.handle_register)
        card_layout.addWidget(btn_register)
        
        btn_goto_login = QPushButton("Back to Log In")
        btn_goto_login.setObjectName("SecondaryButton")
        btn_goto_login.clicked.connect(lambda: self.setCurrentWidget(self.login_widget))
        card_layout.addWidget(btn_goto_login)
        
        layout.addWidget(card)

    def handle_login(self):
        """Processes authentication credentials."""
        username = self.login_user_input.text().strip()
        password = self.login_pass_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Validation Error", "Please fill in all fields.")
            return
            
        user = self.db.get_user_by_username(username)
        if not user:
            # Fallback check for email login
            user = self.db.get_user_by_email(username)
            
        if user and verify_password(password, user["password_hash"]):
            logger.info(f"User login successful: {user['username']}")
            # Clear inputs
            self.login_user_input.clear()
            self.login_pass_input.clear()
            self.login_successful.emit(user["id"], user["username"], user["email"])
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password.")

    def handle_register(self):
        """Processes account creation with security validations."""
        username = self.reg_user_input.text().strip()
        email = self.reg_email_input.text().strip()
        password = self.reg_pass_input.text()
        password_confirm = self.reg_pass_confirm.text()
        
        # Validations
        if not username or not email or not password or not password_confirm:
            QMessageBox.warning(self, "Validation Error", "All fields are required.")
            return
            
        if not validate_username(username):
            QMessageBox.warning(self, "Validation Error", "Username must be 3-20 alphanumeric characters or underscores.")
            return
            
        if not validate_email(email):
            QMessageBox.warning(self, "Validation Error", "Please enter a valid email address.")
            return
            
        if password != password_confirm:
            QMessageBox.warning(self, "Validation Error", "Passwords do not match.")
            return
            
        is_strong, strength_err = check_password_strength(password)
        if not is_strong:
            QMessageBox.warning(self, "Password Weak", strength_err)
            return

        # Check uniqueness in DB
        if self.db.get_user_by_username(username):
            QMessageBox.warning(self, "Account Exists", "This username is already taken.")
            return
            
        if self.db.get_user_by_email(email):
            QMessageBox.warning(self, "Account Exists", "This email address is already registered.")
            return

        # Hash and save
        hashed = hash_password(password)
        user_id = self.db.create_user(username, email, hashed)
        
        if user_id != -1:
            QMessageBox.information(self, "Success", "Account created successfully! Please log in.")
            # Clear fields and redirect
            self.reg_user_input.clear()
            self.reg_email_input.clear()
            self.reg_pass_input.clear()
            self.reg_pass_confirm.clear()
            self.setCurrentWidget(self.login_widget)
        else:
            QMessageBox.critical(self, "Error", "An error occurred creating your account. Please try again.")
class AuthController:
    """Helper class if needed to orchestrate model actions."""
    pass
