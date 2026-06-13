# System Architecture Document

This document outlines the system architecture and internal components of the Aura Health Application. The system is designed following the **Model-View-Controller (MVC)** design pattern, supplemented by a **Service Layer** to isolate domain-specific tasks.

---

## 1. High-Level Component Diagram
The diagram below illustrates the separation between the presentation layer, business logic services, and the data access layers:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                            │
│   (PyQt5 Views)                                                         │
│                                                                         │
│   ┌──────────┐   ┌─────────────┐   ┌────────────┐   ┌────────────────┐  │
│   │ AuthView │   │DashboardView│   │ UploadView │   │  HistoryView   │  │
│   └────┬─────┘   └──────┬──────┘   └─────┬──────┘   └───────┬────────┘  │
│        │                │                │                  │           │
│   ┌────▼─────┐   ┌──────▼──────┐   ┌─────▼──────┐   ┌───────▼────────┐  │
│   │ OCRView  │   │AnalysisView │   │ Styles (QSS)│   │  MainWindow    │  │
│   └──────────┘   └─────────────┘   └────────────┘   └───────┬────────┘  │
└─────────────────────────────────────────────────────────────┼───────────┘
                                                              │
                                                     Emits events & forwards
                                                              │
┌─────────────────────────────────────────────────────────────▼───────────┐
│                              SERVICE LAYER                              │
│   (Business Logic)                                                      │
│                                                                         │
│   ┌────────────────┐   ┌───────────────────┐   ┌────────────────────┐   │
│   │   OCRService   │   │ ExtractionService │   │  AnalysisService   │   │
│   │ (OpenCV/Tess)  │   │  (spaCy/Regex)    │   │ (Clinical Ranges)  │   │
│   └────────────────┘   └───────────────────┘   └────────────────────┘   │
│   ┌────────────────┐   ┌───────────────────┐                            │
│   │   AIService    │   │ PDFExportService  │                            │
│   │ (Local Ollama) │   │   (ReportLab)     │                            │
│   └────────────────┘   └───────────────────┘                            │
└─────────────────────────────────────────────────────────────┬───────────┘
                                                              │
                                                     SQL queries & CRUD
                                                              │
┌─────────────────────────────────────────────────────────────▼───────────┐
│                               DATA LAYER                                │
│   (SQLite)                                                              │
│                                                                         │
│                 ┌───────────────────────────────────────┐               │
│                 │               DBManager               │               │
│                 └──────────────────┬────────────────────┘               │
│                                    │                                    │
│                 ┌──────────────────▼────────────────────┐               │
│                 │         medical_analysis.db           │               │
│                 └───────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Modules Architecture

### Frontend Layer (Views)
- **MainWindow (`main_window.py`)**: Houses the application frame, routing, and user sessions. Observes events from views and calls appropriate service classes.
- **AuthView (`auth_view.py`)**: Gathers and validates credentials.
- **DashboardView (`dashboard_view.py`)**: Combines descriptive statistics cards with Matplotlib canvas drawing.
- **UploadView (`upload_view.py`)**: Implements PyQt `setAcceptDrops(True)` to receive file pointer URLs.
- **OCRView (`ocr_view.py`)**: Triggers an asynchronous QThread worker (`OCRWorker`) to keep UI threads responsive while running heavy OpenCV operations and Tesseract execution.
- **AnalysisView (`analysis_view.py`)**: Spawns `AIWorker` to run Ollama summaries asynchronously. Renders cells with custom colored status tags.
- **HistoryView (`history_view.py`)**: Handles table generation from filtered SQLite database queries.

### Service Layer (Business Logic)
- **OCRService**: Focuses on image quality enhancement. Normalizes PDF rendering by using PyMuPDF to convert PDF structures into image arrays in-memory, avoiding Windows-incompatible binaries.
- **ExtractionService**: Pairs spaCy's tokenizer with regular expression captures to detect and normalize numbers, names, and formats (e.g., converting WBC/platelet formats, splitting Blood Pressure).
- **AnalysisService**: Encapsulates clinical guidelines. Evaluates boundaries for ranges (Normal, Low, High, Critical) and returns text representation ranges.
- **AIService**: Orchestrates local AI responses. Contacts the Ollama API, but retains an offline rule-based fallback if the engine is stopped.
- **PDFExportService**: Packages document layouts using ReportLab to write PDF grids on disk.

### Data Layer
- **DBManager**: Connects views and services to SQLite. Provides automatic schema setup on first application boot.
