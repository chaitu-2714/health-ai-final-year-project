import os
import sys
import subprocess
import shutil

def main():
    print("=== Aura Health Standalone Executable Builder ===")
    print("This script compiles the application into a single executable using PyInstaller.")

    # 1. Ensure pyinstaller is installed
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
    except ImportError:
        print("Installing pyinstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 2. Define command line arguments
    # Include src directory and package dependencies as hidden imports
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--clean",
        "--name=AuraHealth",
        "--onefile",  # Packages everything into a single .exe
        "--add-data=src;src",  # Include source files
        "--hidden-import=fitz",
        "--hidden-import=spacy",
        "--hidden-import=matplotlib",
        "--hidden-import=reportlab",
        "--hidden-import=cv2",
        "--hidden-import=pytesseract",
        "--hidden-import=sqlite3",
        "--hidden-import=requests",
        "--hidden-import=numpy",
        "app.py"
    ]

    print(f"Executing build command: {' '.join(cmd)}")
    
    # Run process
    try:
        subprocess.check_call(cmd)
        print("\n==============================================")
        print("Success! Standalone build completed successfully.")
        print(f"Executable is located at: {os.path.join(os.getcwd(), 'dist', 'AuraHealth.exe')}")
        print("==============================================")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with exit code: {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
