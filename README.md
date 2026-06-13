# Aura Health: Offline AI-Powered Medical Report Analysis System

Aura Health is a production-ready, fully offline desktop application built with Python and PyQt5. It allows users to upload medical reports (PDF or images), process them using OpenCV computer vision and Tesseract OCR, parse clinical parameters (like Hemoglobin, WBC, Blood Sugar, Cholesterol, and Blood Pressure) using spaCy NLP and regular expressions, evaluate values against clinical ranges (Normal, Low, High, Critical), and draft summaries using a local Ollama AI engine. All operations execute completely locally on Windows to maintain absolute patient privacy.

---

## Key Features
- **Strict MVC Architecture**: Decoupled presentation, service, and database access layers.
- **Asynchronous Workers**: Heavy tasks (OpenCV preprocessing, OCR, Ollama AI) run on background threads (`QThread`) to prevent user interface freezes.
- **CV Image Enhancement**: Grayscale conversion, bilateral noise filtering, and Otsu's binarization.
- **Hybrid Parser**: Combines token-level spaCy Matcher with custom regular expressions for parameters.
- **Local LLM Summary**: Integrates with local Ollama APIs (using Gemma or Llama).
- **Rule-Based Fallback**: Swaps to a local medical summary generator if Ollama is offline.
- **Matplotlib Trend Plotting**: Renders line charts tracking lab values over time.
- **History Audit Logs**: Fully queryable database log to search, view details, export PDFs via ReportLab, or perform cascade deletions.
- **Light and Dark Modes**: Dynamic theme transitions across all widgets.

---

## Directory Structure
```
e:/health/
│   app.py                      # Application Launcher Entry Point
│   requirements.txt            # Package Dependencies
│   README.md                   # Setup and Documentation Guide
│
├───src/
│   ├───database/
│   │       db_manager.py       # SQLite connection and query executions
│   │
│   ├───services/
│   │       ocr_service.py      # PDF/image processing and PyTesseract OCR
│   │       extraction_service.py # spaCy and Regex data extractor
│   │       analysis_service.py # Standard normal range comparison engine
│   │       ai_service.py       # Ollama API and rule-based fallback writer
│   │       pdf_export.py       # ReportLab PDF report generation
│   │
│   ├───ui/
│   │       styles.py           # Light and Dark mode QSS stylesheets
│   │       main_window.py      # App frame shell and page navigation router
│   │       auth_view.py        # Salted login and registration panels
│   │       dashboard_view.py   # Metrics cards and Matplotlib line charts
│   │       upload_view.py      # Drag-and-drop file upload zone
│   │       ocr_view.py         # Document preview and raw text verifier
│   │       analysis_view.py    # Parameters breakdown table and AI summary
│   │       history_view.py     # History log tables with search/date filters
│   │
│   └───utils/
│           helpers.py          # Hashing cryptography, validations, size checks
│           logger.py           # Logging module (console and file logs)
│
├───samples/                    # Sample laboratory files
│       generate_samples.py     # Script to generate test data
│
└───docs/                       # Documentation files
        db_schema.md            # Table schemas
        architecture.md         # Component diagrams
        er_diagram.md           # ER database mappings
        data_flow.md            # Context and level-1 flow maps
        use_cases.md            # Use case descriptions and diagrams
        research_paper.md       # AI/OCR Healthcare research outline
        presentation.md         # Presentation slides outline
```

---

## Installation & Setup Guide (Windows)

Follow these steps to set up and run the application:

### Step 1: Install Python
Ensure Python (version 3.10 or 3.11 recommended) is installed on your Windows machine and added to your system `PATH`.

### Step 2: Install Tesseract OCR
1. Download the Windows installer for Tesseract OCR from [UB Mannheim GitHub Releases](https://github.com/UB-Mannheim/tesseract/wiki).
2. Run the installer and note down the path (default is `C:\Program Files\Tesseract-OCR\tesseract.exe`).
3. Add the Tesseract directory (`C:\Program Files\Tesseract-OCR`) to your system environment variables `PATH`.
4. *Note: The application includes auto-detection code to search standard locations, but adding it to your system PATH ensures seamless operations.*

### Step 3: Set Up Ollama and LLM Models (For AI Summaries)
1. Download and install Ollama for Windows from [Ollama's Official Website](https://ollama.com).
2. Open PowerShell or Command Prompt and run the following command to download a lightweight language model (Gemma 2B is recommended for faster CPU inference):
   ```powershell
   ollama pull gemma2:2b
   ```
   *(Alternatively, you can pull Llama 3: `ollama pull llama3.2:3b` or `ollama pull llama3`)*
3. Keep the Ollama application running in the system tray. The application will connect to it automatically at `http://localhost:11434`.

### Step 4: Install Dependencies
Open PowerShell inside the project directory (`e:\health`) and run:
```powershell
pip install -r requirements.txt
```
If you wish to test spaCy's native model matching (optional), download the English package:
```powershell
python -m spacy download en_core_web_sm
```
*Note: The application uses a blank English vocabulary matcher (`spacy.blank("en")`) out-of-the-box, so downloading a large model is **not required** to run the app offline.*

---

## Run the Application

### 1. Populate Sample Files
First, run the utility script to generate testing reports (both PDF and PNG scans):
```powershell
python samples/generate_samples.py
```
This generates the sample files inside the `samples/` directory.

### 2. Launch App
Start the main application:
```powershell
python app.py
```

---

## Application Usage Walkthrough
1. **Register & Login**: Open the application, click **Create an Account**, register a user, then log in. The passwords are securely encrypted using PBKDF2 cryptography.
2. **Dashboard**: After logging in, the sidebar appears showing the **Dashboard** displaying metric cards (Reports Count, Health Score, Alerts) and historical charts. Since no reports are uploaded initially, a placeholder appears.
3. **Upload Report**: Click **Upload Report** in the sidebar. Select **Browse Files** or drag-and-drop a sample file (e.g. `samples/cbc_abnormal.png` or `samples/cbc_normal.pdf`).
4. **Verify Text (OCR)**: The file is sent to OpenCV (denoising, binarization) and Tesseract OCR. A loading spinner indicates progress. The first page of the document renders on the left, and raw text appears on the right. You can edit this text to correct any scanning errors.
5. **Run Analysis**: Click **Run Clinical Health Analysis**. The system:
   - Registers the report.
   - Extracts Hemoglobin, WBC, Platelets, RBC, Sugar, Cholesterol, and Blood Pressure.
   - Saves records to SQLite.
   - Renders a color-coded parameter status grid.
   - Fetches the Ollama AI summary (or fallbacks) in a background thread.
6. **Export PDF**: Click **Export Report PDF** to save a styled clinical PDF on your disk.
7. **History**: Go to **Report History** in the sidebar. You can search by parameters (e.g., `blood sugar`), filter by classification, or select date ranges. Click **View** to load details, **PDF** to print, or **Delete** to purge.
8. **Theme Toggle**: Switch between **Light Mode** and **Dark Mode** inside the sidebar. Charts and dropboxes update colors dynamically.

---

## Troubleshooting
- **TesseractNotFoundError**: Ensure Tesseract is installed. If installed in a custom location, add it to your environment variables `PATH` or modify the executable path mapping in `src/services/ocr_service.py` (`auto_configure_tesseract` function).
- **Ollama Summary Loading**: If the AI Summary box hangs or displays fallback results, verify that Ollama is running (`ollama run gemma2:2b` or check system tray). The app automatically falls back to rules-based summaries if the server is offline, so operations are unaffected.
