import unittest
import os
import sys

# Ensure project directories are in PATH for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.db_manager import DBManager
from src.utils.helpers import (
    hash_password, verify_password, validate_email, validate_username, check_password_strength
)
from src.services.analysis_service import AnalysisService
from src.services.extraction_service import ExtractionService

class TestDatabaseLayer(unittest.TestCase):
    """Tests the database schema initialization, CRUD operations, and cascade deletions."""
    
    def setUp(self):
        self.test_db_path = "test_medical_analysis.db"
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except OSError:
                pass
        self.db = DBManager(db_path=self.test_db_path)

    def tearDown(self):
        if hasattr(self, 'test_db_path') and os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except OSError:
                pass

    def test_user_creation_and_login(self):
        """Tests that a user is correctly registered, salt-hashed, and retrieved."""
        username = "alex123"
        email = "alex@test.com"
        pw = "SecureP@ss1"
        
        pw_hash = hash_password(pw)
        user_id = self.db.create_user(username, email, pw_hash)
        self.assertNotEqual(user_id, -1)
        
        # Verify fetching
        user_by_name = self.db.get_user_by_username(username)
        self.assertIsNotNone(user_by_name)
        self.assertEqual(user_by_name["email"], email)
        self.assertTrue(verify_password(pw, user_by_name["password_hash"]))

        # Verify duplicate blocks
        dup_id = self.db.create_user(username, "other@test.com", pw_hash)
        self.assertEqual(dup_id, -1)

    def test_report_and_cascade_delete(self):
        """Tests adding reports, parameter data, analysis metrics, and verifying cascade deletion."""
        # 1. Create User
        pw_hash = hash_password("TestPass123!")
        user_id = self.db.create_user("testuser", "test@test.com", pw_hash)
        
        # 2. Add Report
        report_id = self.db.add_report(user_id, "C:\\test\\report.pdf", "pdf")
        self.assertNotEqual(report_id, -1)
        
        # 3. Add Parameters
        param_id = self.db.add_extracted_parameter(report_id, "Hemoglobin", 11.2, "g/dL")
        self.assertNotEqual(param_id, -1)
        
        # 4. Add Classification Result
        analysis_id = self.db.add_analysis_result(report_id, param_id, "Low", "12.0 - 17.5")
        self.assertNotEqual(analysis_id, -1)
        
        # Verify details
        details = self.db.get_report_analysis_details(report_id)
        self.assertEqual(len(details), 1)
        self.assertEqual(details[0]["parameter_name"], "Hemoglobin")
        self.assertEqual(details[0]["classification"], "Low")

        # 5. Delete Report and Verify Cascade
        deleted = self.db.delete_report(report_id, user_id)
        self.assertTrue(deleted)
        
        # Details should now be empty
        empty_details = self.db.get_report_analysis_details(report_id)
        self.assertEqual(len(empty_details), 0)


class TestHelpers(unittest.TestCase):
    """Tests password crypt validation rules and general input matching."""

    def test_cryptography(self):
        pw = "SuperComplexPass!99"
        h = hash_password(pw)
        self.assertTrue(verify_password(pw, h))
        self.assertFalse(verify_password("wrong_pass", h))

    def test_validations(self):
        self.assertTrue(validate_email("test.name+ex@sub.domain.co"))
        self.assertFalse(validate_email("test@domain"))
        
        self.assertTrue(validate_username("valid_user_1"))
        self.assertFalse(validate_username("sh")) # Too short
        self.assertFalse(validate_username("user name")) # Space not allowed

    def test_password_strength(self):
        self.assertTrue(check_password_strength("V@lidP4ssw0rd")[0])
        # Missing uppercase
        self.assertFalse(check_password_strength("invalid_pass_1!")[0])
        # Missing digit
        self.assertFalse(check_password_strength("Invalid_Pass!")[0])
        # Too short
        self.assertFalse(check_password_strength("Sh0rt!")[0])


class TestAnalysisEngine(unittest.TestCase):
    """Tests that medical boundary metrics classify values accurately."""

    def test_hemoglobin(self):
        # Normal
        cls, _ = AnalysisService.analyze_parameter("Hemoglobin", 14.5)
        self.assertEqual(cls, "Normal")
        # Low
        cls, _ = AnalysisService.analyze_parameter("Hemoglobin", 11.2)
        self.assertEqual(cls, "Low")
        # Critical Low
        cls, _ = AnalysisService.analyze_parameter("Hemoglobin", 7.5)
        self.assertEqual(cls, "Critical")
        # High
        cls, _ = AnalysisService.analyze_parameter("Hemoglobin", 18.2)
        self.assertEqual(cls, "High")

    def test_blood_sugar(self):
        # Normal
        cls, _ = AnalysisService.analyze_parameter("Blood Sugar", 90)
        self.assertEqual(cls, "Normal")
        # High
        cls, _ = AnalysisService.analyze_parameter("Blood Sugar", 130)
        self.assertEqual(cls, "High")
        # Critical High
        cls, _ = AnalysisService.analyze_parameter("Blood Sugar", 260)
        self.assertEqual(cls, "Critical")

    def test_new_parameters_classification(self):
        # Vitamin D3
        cls, _ = AnalysisService.analyze_parameter("Vitamin D3", 45.0)
        self.assertEqual(cls, "Normal")
        cls, _ = AnalysisService.analyze_parameter("Vitamin D3", 22.0)
        self.assertEqual(cls, "Low")
        cls, _ = AnalysisService.analyze_parameter("Vitamin D3", 8.0)
        self.assertEqual(cls, "Critical")

        # Vitamin B12
        cls, _ = AnalysisService.analyze_parameter("Vitamin B12", 500.0)
        self.assertEqual(cls, "Normal")
        cls, _ = AnalysisService.analyze_parameter("Vitamin B12", 150.0)
        self.assertEqual(cls, "Low")
        cls, _ = AnalysisService.analyze_parameter("Vitamin B12", 80.0)
        self.assertEqual(cls, "Critical")

        # Thyroid TSH
        cls, _ = AnalysisService.analyze_parameter("Thyroid TSH", 2.1)
        self.assertEqual(cls, "Normal")
        cls, _ = AnalysisService.analyze_parameter("Thyroid TSH", 0.3)
        self.assertEqual(cls, "Low")
        cls, _ = AnalysisService.analyze_parameter("Thyroid TSH", 5.2)
        self.assertEqual(cls, "High")
        cls, _ = AnalysisService.analyze_parameter("Thyroid TSH", 11.5)
        self.assertEqual(cls, "Critical")


class TestExtractionEngine(unittest.TestCase):
    """Tests regex and spaCy parser rules against simulated OCR strings."""

    def setUp(self):
        self.extractor = ExtractionService()

    def test_structured_report_parsing(self):
        raw_ocr = """
        METROPOLITAN DIAGNOSTIC CENTRE
        Date: 2026-06-12
        Patient: John Doe
        
        TEST RESULTS:
        HEMOGLOBIN ---------- 13.8 g/dL  (Range: 12.0 - 17.5)
        RBC Count ----------- 5.2 million/mcL (Range: 4.2 - 5.9)
        WBC Count ----------- 8.5 x10^3/uL (Range: 4.5 - 11.0)
        Platelets ----------- 220,000 /mcL (Range: 150 - 450)
        Fasting Glucose ----- 95 mg/dL (Range: 70 - 100)
        Total Cholesterol --- 215 mg/dL (Range: < 200)
        Blood Pressure ------ 125/82 mmHg
        Vitamin D3 ---------- 42.5 ng/mL
        Vitamin B12 --------- 650 pg/mL
        TSH ----------------- 2.45 uIU/mL
        """
        params = self.extractor.extract_parameters(raw_ocr)
        param_dict = {p["parameter_name"]: p for p in params}

        self.assertIn("Hemoglobin", param_dict)
        self.assertEqual(param_dict["Hemoglobin"]["value"], 13.8)

        self.assertIn("RBC", param_dict)
        self.assertEqual(param_dict["RBC"]["value"], 5.2)

        self.assertIn("WBC", param_dict)
        self.assertEqual(param_dict["WBC"]["value"], 8.5)

        # Platelet comma removal check
        self.assertIn("Platelets", param_dict)
        self.assertEqual(param_dict["Platelets"]["value"], 220) # 220,000 -> 220 x10^3/uL standard

        self.assertIn("Blood Sugar", param_dict)
        self.assertEqual(param_dict["Blood Sugar"]["value"], 95)

        self.assertIn("Cholesterol", param_dict)
        self.assertEqual(param_dict["Cholesterol"]["value"], 215)

        # Blood pressure splits check
        self.assertIn("Systolic Blood Pressure", param_dict)
        self.assertEqual(param_dict["Systolic Blood Pressure"]["value"], 125)
        self.assertIn("Diastolic Blood Pressure", param_dict)
        self.assertEqual(param_dict["Diastolic Blood Pressure"]["value"], 82)

        self.assertIn("Vitamin D3", param_dict)
        self.assertEqual(param_dict["Vitamin D3"]["value"], 42.5)

        self.assertIn("Vitamin B12", param_dict)
        self.assertEqual(param_dict["Vitamin B12"]["value"], 650)

        self.assertIn("Thyroid TSH", param_dict)
        self.assertEqual(param_dict["Thyroid TSH"]["value"], 2.45)


if __name__ == "__main__":
    unittest.main()
