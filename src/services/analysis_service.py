import logging

logger = logging.getLogger("MedicalApp.AnalysisService")

class AnalysisService:
    """Classifies extracted medical parameters against standard reference ranges."""

    # Reference Ranges Configurations
    # Format: { parameter_name: { "range_text": str, "classify_fn": function } }
    @staticmethod
    def classify_hemoglobin(val: float) -> str:
        if val < 8.0 or val > 20.0:
            return "Critical"
        elif val < 12.0:
            return "Low"
        elif val > 17.5:
            return "High"
        return "Normal"

    @staticmethod
    def classify_rbc(val: float) -> str:
        if val < 3.0 or val > 7.0:
            return "Critical"
        elif val < 4.2:
            return "Low"
        elif val > 5.9:
            return "High"
        return "Normal"

    @staticmethod
    def classify_wbc(val: float) -> str:
        if val < 2.0 or val > 30.0:
            return "Critical"
        elif val < 4.5:
            return "Low"
        elif val > 11.0:
            return "High"
        return "Normal"

    @staticmethod
    def classify_platelets(val: float) -> str:
        if val < 50.0 or val > 1000.0:
            return "Critical"
        elif val < 150.0:
            return "Low"
        elif val > 450.0:
            return "High"
        return "Normal"

    @staticmethod
    def classify_blood_sugar(val: float) -> str:
        if val < 50.0 or val > 250.0:
            return "Critical"
        elif val < 70.0:
            return "Low"
        elif val > 100.0:
            return "High"
        return "Normal"

    @staticmethod
    def classify_cholesterol(val: float) -> str:
        if val >= 240.0:
            return "Critical"
        elif val >= 200.0:
            return "High"
        # Total cholesterol does not usually have a "low" clinical concern unless extremely low
        elif val < 100.0:
            return "Low"
        return "Normal"

    @staticmethod
    def classify_systolic_bp(val: float) -> str:
        if val >= 180.0 or val < 80.0:
            return "Critical"
        elif val >= 120.0:
            return "High"
        elif val < 90.0:
            return "Low"
        return "Normal"

    @staticmethod
    def classify_diastolic_bp(val: float) -> str:
        if val >= 120.0 or val < 50.0:
            return "Critical"
        elif val >= 80.0:
            return "High"
        elif val < 60.0:
            return "Low"
        return "Normal"

    @staticmethod
    def classify_vit_d3(val: float) -> str:
        if val < 10.0 or val > 150.0:
            return "Critical"
        elif val < 30.0:
            return "Low"
        elif val > 100.0:
            return "High"
        return "Normal"

    @staticmethod
    def classify_vit_b12(val: float) -> str:
        if val < 100.0 or val > 1500.0:
            return "Critical"
        elif val < 200.0:
            return "Low"
        elif val > 900.0:
            return "High"
        return "Normal"

    @staticmethod
    def classify_tsh(val: float) -> str:
        if val < 0.10 or val > 10.0:
            return "Critical"
        elif val < 0.40:
            return "Low"
        elif val > 4.50:
            return "High"
        return "Normal"

    @classmethod
    def analyze_parameter(cls, name: str, value: float) -> tuple:
        """
        Analyzes a parameter value and returns (classification, reference_range_text).
        Classifications can be: 'Normal', 'Low', 'High', 'Critical'
        """
        name_lower = name.lower()
        
        # Default fallback
        classification = "Normal"
        ref_range = "N/A"

        if "hemoglobin" in name_lower or name_lower == "hgb":
            ref_range = "12.0 - 17.5 g/dL"
            classification = cls.classify_hemoglobin(value)
            
        elif "rbc" in name_lower:
            ref_range = "4.2 - 5.9 million/mcL"
            classification = cls.classify_rbc(value)
            
        elif "wbc" in name_lower:
            ref_range = "4.5 - 11.0 x10^3/uL"
            classification = cls.classify_wbc(value)
            
        elif "platelet" in name_lower or name_lower == "plt":
            ref_range = "150 - 450 x10^3/uL"
            classification = cls.classify_platelets(value)
            
        elif "blood sugar" in name_lower or "glucose" in name_lower or name_lower == "fbs":
            ref_range = "70 - 100 mg/dL"
            classification = cls.classify_blood_sugar(value)
            
        elif "cholesterol" in name_lower:
            ref_range = "< 200 mg/dL"
            classification = cls.classify_cholesterol(value)
            
        elif "systolic" in name_lower:
            ref_range = "< 120 mmHg"
            classification = cls.classify_systolic_bp(value)
            
        elif "diastolic" in name_lower:
            ref_range = "< 80 mmHg"
            classification = cls.classify_diastolic_bp(value)

        elif "vitamin d3" in name_lower or name_lower == "vit d3" or "vitamin d" in name_lower:
            ref_range = "30.0 - 100.0 ng/mL"
            classification = cls.classify_vit_d3(value)
            
        elif "vitamin b12" in name_lower or name_lower == "vit b12" or "b12" in name_lower:
            ref_range = "200.0 - 900.0 pg/mL"
            classification = cls.classify_vit_b12(value)
            
        elif "tsh" in name_lower or "thyroid" in name_lower:
            ref_range = "0.40 - 4.50 uIU/mL"
            classification = cls.classify_tsh(value)

        logger.info(f"Analyzed {name} (Value: {value}) -> Classification: {classification}, Range: {ref_range}")
        return classification, ref_range
