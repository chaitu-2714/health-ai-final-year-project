# Use Case Documentation

This document describes the use cases detailing the user interactions, system behaviors, preconditions, and success flows.

---

## 1. Use Case Diagram
The diagram below maps user roles to system use case boundaries:

```mermaid
left_to_right_direction
actor User

rectangle "Aura Medical Report System" {
    User --> (Register Account)
    User --> (Log In)
    User --> (View Dashboard Trends)
    User --> (Upload Lab Report)
    User --> (Verify OCR Text)
    User --> (Analyze Parameters)
    User --> (View AI Summary)
    User --> (Export Analysis PDF)
    User --> (Search & Filter History)
    User --> (Delete History Report)
    User --> (Toggle Dark/Light Mode)
}
```

---

## 2. Core Use Case Descriptions

### Use Case 1: Upload & Analyze Medical Report
- **Actor**: User
- **Preconditions**: User must be registered, logged in, and have a valid lab report file.
- **Main Flow**:
  1. User navigates to the **Upload Report** view.
  2. User drags and drops or browses to select a file (`.pdf`, `.png`, `.jpg`, `.tiff`).
  3. System validates file size and format.
  4. System binarizes and denoises the file using OpenCV, then performs Tesseract OCR in a background thread while displaying a loading progress bar.
  5. System presents the raw text in an editable pane.
  6. User verifies the text, types manual adjustments if needed, and clicks **Run Clinical Health Analysis**.
  7. System saves the report, runs extraction (spaCy/Regex), compares values against reference ranges, saves results, and displays the analysis screen.
  8. System queries the local Ollama instance (or falls back to templates) to generate the summary.
- **Alternative Flow (Offline Fallback)**:
  - If Ollama is offline or unreachable, the system automatically uses a rule-based parser to construct a structured clinical summary statement.
- **Postconditions**: The report metadata, biometric parameters, classifications, and audit history log are successfully committed to the SQLite database.

### Use Case 2: Query History & Export PDF
- **Actor**: User
- **Preconditions**: User must have previously processed reports in their profile.
- **Main Flow**:
  1. User navigates to the **Report History** view.
  2. User inputs a keyword (e.g. `Hemoglobin`) or changes date filter values.
  3. System dynamically refreshes and shows matching results.
  4. User clicks **PDF** next to a report row.
  5. User designates a path in the file save dialog.
  6. System creates a formatted Letter-sized PDF with clinical headers, parameters table, color-coded badges, and AI summary, saving it to disk.
  7. System appends an audit record to the `History` table.
- **Postconditions**: A PDF report is written to disk, and the history table logs the export.
