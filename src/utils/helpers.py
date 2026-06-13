import hashlib
import os
import re
import logging

logger = logging.getLogger("MedicalApp.Helpers")

def hash_password(password: str) -> str:
    """Hashes a password using PBKDF2-HMAC-SHA256 with a unique random salt."""
    salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"{salt.hex()}${pw_hash.hex()}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verifies a password against a stored PBKDF2 hash."""
    try:
        if "$" not in stored_hash:
            return False
        salt_hex, hash_hex = stored_hash.split("$")
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
        pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return pw_hash == expected_hash
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False

def validate_email(email: str) -> bool:
    """Validates an email address format."""
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(email_regex, email.strip()))

def validate_username(username: str) -> bool:
    """Validates username format (alphanumeric, length 3-20)."""
    username_regex = r"^[a-zA-Z0-9_]{3,20}$"
    return bool(re.match(username_regex, username.strip()))

def check_password_strength(password: str) -> tuple:
    """
    Checks password complexity.
    Returns (is_strong, error_message).
    Requirements:
    - At least 8 characters long
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character (e.g. !@#$%^&*)."
    return True, ""

def get_file_type(file_path: str) -> str:
    """Returns the file extension without the dot, lowercase."""
    _, ext = os.path.splitext(file_path)
    return ext.replace(".", "").lower()

def is_valid_file(file_path: str) -> bool:
    """Checks if the file exists, has a valid extension, and is within size limits (10MB)."""
    if not os.path.exists(file_path):
        return False
    
    ext = get_file_type(file_path)
    if ext not in ["pdf", "png", "jpg", "jpeg", "tiff"]:
        return False
        
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if size_mb > 10.0:
        return False
        
    return True

# --- Config JSON Helper Functions ---

import json

DEFAULT_CONFIG = {
    "tesseract_path": r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    "ollama_url": "http://localhost:11434",
    "ollama_model": "gemma2:2b",
    "dark_mode": False
}

def get_config_path() -> str:
    """Returns the absolute path to config.json in the project root."""
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(root_dir, "config.json")

def get_config() -> dict:
    """Reads config.json, creating it with defaults if missing."""
    path = get_config_path()
    if not os.path.exists(path):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
            # Ensure all default keys exist
            updated = False
            for k, v in DEFAULT_CONFIG.items():
                if k not in config:
                    config[k] = v
                    updated = True
            if updated:
                save_config(config)
            return config
    except Exception as e:
        logger.error(f"Failed to load config.json: {e}. Returning defaults.")
        return DEFAULT_CONFIG.copy()

def save_config(config: dict) -> bool:
    """Saves configuration dictionary to config.json."""
    path = get_config_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        logger.info(f"Saved config.json to: {path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save config.json: {e}")
        return False
