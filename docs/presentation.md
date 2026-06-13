# PowerPoint Presentation Outline

**Project Title**: Aura Health: An Offline, AI-Powered Clinical Medical Report Analysis System  
**Presentation Target**: Final-Year Academic Project Demonstration  

---

### Slide 1: Title Slide
- **Content**: 
  - Project Title: Aura Health System
  - Subtitle: Offline AI-Powered Medical Report Digitization and Analytics
  - Presenter Name(s) & Department
  - Institution Name & Academic Adviser Name

### Slide 2: Project Background & Problem Statement
- **Key Points**:
  - Medical reports are locked in static structures (paper, scanned PDFs).
  - Cloud-based medical digitizers expose sensitive Protected Health Information (PHI) to data breaches.
  - Compliance with HIPAA (Health Insurance Portability and Accountability Act) and GDPR requires localized data handling.
- **The Solution**: A production-grade, 100% offline desktop application that processes, classifies, logs, and summarizes medical laboratory reports locally.

### Slide 3: Project Objectives
- **Key Goals**:
  - Implement computer vision image enhancements to optimize OCR extraction.
  - Combine rule-based NLP (spaCy) and regular expressions for lab parameters.
  - Automatically analyze values against clinical reference limits.
  - Deploy local LLMs (Ollama) to draft medical narratives safely.
  - Retain audit logs, trend metrics, and enable PDF summaries.

### Slide 4: System Architecture (MVC Pattern)
- **Frameworks Used**:
  - **View**: PyQt5 (Desktop Interface), Matplotlib (Trend Plots)
  - **Controller / Service Layer**: OpenCV (CV), PyMuPDF (PDF Parser), Tesseract (OCR), spaCy (NLP), Ollama (Local AI), ReportLab (PDF Writer)
  - **Model / Data**: SQLite (Local Database File)
- **Visual**: Block diagram showing MVC data cycles.

### Slide 5: Database Schema Layout
- **Tables Designed**:
  - `Users`: Secured with salted PBKDF2 cryptography.
  - `Reports`: Relational tracker of files.
  - `ExtractedParameters`: Stores parsed numeric metrics and units.
  - `AnalysisResults`: Flags Normal, Low, High, Critical statuses.
  - `History`: Audits actions with search and delete triggers.
- **Design Highlight**: Foreign key constraints with `ON DELETE CASCADE` prevent database fragmentation.

### Slide 6: Image Processing & OCR Pipeline
- **Methodology**:
  - Page Conversion: PyMuPDF parses digital text or converts scanned pages in-memory (eliminating external Poppler requirements).
  - Image Cleanup: Bilateral edge preservation filtering, grayscale conversion, and Otsu's optimal thresholding.
  - Character Recognition: Tesseract engine maps characters to editable strings.

### Slide 7: Parameter Extraction & Clinical Range Engine
- **Extraction Logic**:
  - spaCy token pattern matcher catches parameters near numeric tokens.
  - Regex captures complex groupings, decimals, and fractional blood pressure coordinates.
  - Standardizes raw data (e.g. converting WBC and platelet unit differences).
- **Classification Engine**:
  - Parameters (Hemoglobin, RBC, WBC, Platelets, Sugar, Cholesterol, Blood Pressure) are classified (Normal, Low, High, Critical) using standard boundaries.

### Slide 8: Local AI Summary Module
- **Mechanism**:
  - Queries local Ollama API for Gemma 2B or Llama 3 models.
  - Feeds structured parameters to generate concise diagnostic summaries.
- **Uptime Assurance**:
  - Features an instant local rule-based template fallback system, ensuring complete functionality even if the Ollama engine is stopped.

### Slide 9: UI/UX Features & Demonstrations
- **Key UI Components**:
  - Sleek modern sidebar layout.
  - Light Mode and Dark Mode theme toggling.
  - Background QThread workers preventing UI freeze during heavy processing.
  - Interactive Matplotlib charts tracking parameters over time.

### Slide 10: Project Results & Deliverables
- **What has been built**:
  - Complete modular Python codebase (`app.py`, `src/`).
  - Automatically initializing database file.
  - Realistic PDF and PNG test reports in the `samples/` directory.
  - Exportable PDFs generated using ReportLab.

### Slide 11: Security & Compliance Summary
- **Privacy Highlights**:
  - 100% Offline execution ensures compliance with data protection laws.
  - Encryption using local hashing algorithms.
  - Full data ownership, enabling users to purge records completely.

### Slide 12: Future Work & Conclusion
- **Future Directions**:
  - Train localized custom medical vision-language models (VLMs) for direct page-to-JSON parsing.
  - Build cross-platform compilation packages for easy installation.
  - Integrate wearable sensor APIs (e.g., Apple Health, Fitbit) to compare lab values against real-time patient heart rates.
- **Q&A Session**: Floor opened for questions.
