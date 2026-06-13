# Database Schema Documentation

This document describes the structure of the SQLite database (`medical_analysis.db`) used in the Aura Health Application. The database is initialized automatically on startup.

---

## 1. Table: Users
Stores user credentials for application registration and login access. Passwords are encrypted using salted PBKDF2-HMAC-SHA256.

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique user identifier. |
| `username` | TEXT | UNIQUE, NOT NULL | Alphanumeric account username (3-20 chars). |
| `email` | TEXT | UNIQUE, NOT NULL | Valid user email address. |
| `password_hash` | TEXT | NOT NULL | Salted PBKDF2 hash of the password (`salt$hash`). |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date and time of user registration. |

---

## 2. Table: Reports
Maintains references to uploaded medical report files (PDF and images).

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique report identifier. |
| `user_id` | INTEGER | FOREIGN KEY, NOT NULL | References `Users(id)`. Deletes on user cascade. |
| `file_path` | TEXT | NOT NULL | Absolute local filesystem path to the file. |
| `upload_date` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date and time the file was analyzed. |
| `file_type` | TEXT | NOT NULL | Extension abbreviation (e.g. `pdf`, `png`, `jpg`, `tiff`). |

---

## 3. Table: ExtractedParameters
Contains individual laboratory values extracted from the report text by the spaCy/Regex engines.

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique parameter record identifier. |
| `report_id` | INTEGER | FOREIGN KEY, NOT NULL | References `Reports(id)`. Deletes on report cascade. |
| `parameter_name` | TEXT | NOT NULL | Parameter name (e.g. `Hemoglobin`, `Blood Sugar`). |
| `value` | REAL | NOT NULL | Numeric observed value of the parameter. |
| `unit` | TEXT | NOT NULL | Measurement unit standard (e.g. `g/dL`, `mg/dL`). |
| `extracted_date` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp when extraction was run. |

---

## 4. Table: AnalysisResults
Stores the diagnostic classification results of each parameter compared to clinical guidelines.

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique analysis identifier. |
| `report_id` | INTEGER | FOREIGN KEY, NOT NULL | References `Reports(id)`. Deletes on report cascade. |
| `parameter_id` | INTEGER | FOREIGN KEY, NOT NULL | References `ExtractedParameters(id)`. Deletes on cascade. |
| `classification` | TEXT | NOT NULL | Evaluation status: `Normal`, `Low`, `High`, `Critical`. |
| `reference_range` | TEXT | NOT NULL | Standard normal bounds string (e.g. `12.0 - 17.5 g/dL`). |
| `analysis_date` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp when classifications were generated. |

---

## 5. Table: History
Provides a queryable audit trail of user actions within the application.

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique audit log identifier. |
| `user_id` | INTEGER | FOREIGN KEY, NOT NULL | References `Users(id)`. Deletes on user cascade. |
| `report_id` | INTEGER | FOREIGN KEY, NOT NULL | References `Reports(id)`. Deletes on report cascade. |
| `action` | TEXT | NOT NULL | Description of activity: `Uploaded Report`, `Exported PDF`. |
| `timestamp` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date and time the action occurred. |

---

## Relationships & Integrity
- **One-to-Many Relationships**:
  - `Users` ➔ `Reports` (One user can upload multiple reports)
  - `Users` ➔ `History` (One user can have multiple action logs)
  - `Reports` ➔ `ExtractedParameters` (One report yields multiple laboratory values)
  - `Reports` ➔ `AnalysisResults` (One report yields multiple parameter analysis records)
  - `Reports` ➔ `History` (One report can reference multiple historical events)
  - `ExtractedParameters` ➔ `AnalysisResults` (Each parameter has exactly one classification result)
- **Cascade Deletes**:
  - Setting `ON DELETE CASCADE` ensures that deleting a user deletes all associated reports, history logs, parameter metrics, and analysis results automatically, keeping the database clean.
