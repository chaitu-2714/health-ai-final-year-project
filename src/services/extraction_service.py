import re
import logging

# Fallback spaCy import
try:
    import spacy
    from spacy.matcher import Matcher
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    Matcher = None
    logger_spacy = logging.getLogger("MedicalApp.SpacyCheck")
    logger_spacy.warning("spaCy is not installed. Relying on Regex extractor.")

logger = logging.getLogger("MedicalApp.ExtractionService")

class ExtractionService:
    """Extracts medical parameters from OCR text using spaCy and Regular Expressions."""

    def __init__(self):
        self.nlp = None
        self.matcher = None
        if SPACY_AVAILABLE:
            try:
                # Use standard blank English model (extremely lightweight, no download required)
                self.nlp = spacy.blank("en")
                self.matcher = Matcher(self.nlp.vocab)
                self._setup_spacy_matcher()
            except Exception as e:
                logger.error(f"Error initializing spaCy: {e}. Falling back to Regex.")

    def _setup_spacy_matcher(self):
        """Configures patterns for token-based matching in spaCy."""
        # Hemoglobin pattern: HGB/Hemoglobin followed by optional punctuation/preposition and number
        hb_pattern = [
            {"LOWER": {"IN": ["hemoglobin", "hgb", "hb"]}},
            {"IS_PUNCT": True, "OP": "?"},
            {"LIKE_NUM": True}
        ]
        self.matcher.add("HEMOGLOBIN", [hb_pattern])

        # RBC pattern
        rbc_pattern = [
            {"LOWER": {"IN": ["rbc", "red blood cell", "red blood cells"]}},
            {"IS_PUNCT": True, "OP": "?"},
            {"LIKE_NUM": True}
        ]
        self.matcher.add("RBC", [rbc_pattern])

        # WBC pattern
        wbc_pattern = [
            {"LOWER": {"IN": ["wbc", "white blood cell", "white blood cells", "leukocytes"]}},
            {"IS_PUNCT": True, "OP": "?"},
            {"LIKE_NUM": True}
        ]
        self.matcher.add("WBC", [wbc_pattern])

        # Platelets pattern
        plt_pattern = [
            {"LOWER": {"IN": ["platelets", "plt", "platelet"]}},
            {"IS_PUNCT": True, "OP": "?"},
            {"LIKE_NUM": True}
        ]
        self.matcher.add("PLATELETS", [plt_pattern])

        # Glucose pattern
        glucose_pattern = [
            {"LOWER": {"IN": ["glucose", "sugar", "fbs", "fasting glucose"]}},
            {"IS_PUNCT": True, "OP": "?"},
            {"LIKE_NUM": True}
        ]
        self.matcher.add("GLUCOSE", [glucose_pattern])

        # Cholesterol pattern
        chol_pattern = [
            {"LOWER": {"IN": ["cholesterol", "chol"]}},
            {"IS_PUNCT": True, "OP": "?"},
            {"LIKE_NUM": True}
        ]
        self.matcher.add("CHOLESTEROL", [chol_pattern])

        # Vitamin D3 pattern
        vitd_pattern = [
            {"LOWER": {"IN": ["vitamin", "vit"]}},
            {"LOWER": "d3", "OP": "?"},
            {"IS_PUNCT": True, "OP": "?"},
            {"LIKE_NUM": True}
        ]
        self.matcher.add("VITAMIN_D3", [vitd_pattern])

        # Vitamin B12 pattern
        vitb_pattern = [
            {"LOWER": {"IN": ["vitamin", "vit"]}},
            {"LOWER": "b12", "OP": "?"},
            {"IS_PUNCT": True, "OP": "?"},
            {"LIKE_NUM": True}
        ]
        self.matcher.add("VITAMIN_B12", [vitb_pattern])

        # TSH pattern
        tsh_pattern = [
            {"LOWER": {"IN": ["tsh", "thyroid"]}},
            {"IS_PUNCT": True, "OP": "?"},
            {"LIKE_NUM": True}
        ]
        self.matcher.add("TSH", [tsh_pattern])

    def extract_with_regex(self, text: str) -> dict:
        """Extracts parameters using regular expressions. Serves as primary parser and fallback."""
        results = {}

        # Patterns
        patterns = {
            "Hemoglobin": r"(?i)\b(?:hemoglobin|hgb|hb)\b[^\d\n]*(\d+(?:\.\d+)?)\s*(?:g/dl|g/l)?",
            "RBC": r"(?i)\b(?:rbc|red blood cell(?:s)?)\b[^\d\n]*(\d+(?:\.\d+)?)\s*(?:million/mcl|x10\^12/l)?",
            "WBC": r"(?i)\b(?:wbc|white blood cell(?:s)?|leukocytes)\b[^\d\n]*(\d+(?:\.\d+)?)\s*(?:thousand/mcl|cells/mcl|x10\^9/l)?",
            "Platelets": r"(?i)\b(?:platelet(?:s)?|plt|platelet count)\b[^\d\n]*(\d{2,3}(?:,\d{3})?|\d+(?:\.\d+)?)\s*(?:thousand/mcl|/mcl|x10\^9/l)?",
            "Blood Sugar": r"(?i)\b(?:blood sugar|glucose|fasting glucose|fasting blood sugar|fbs)\b[^\d\n]*(\d+(?:\.\d+)?)\s*(?:mg/dl|mmol/l)?",
            "Cholesterol": r"(?i)\b(?:total cholesterol|cholesterol|chol)\b[^\d\n]*(\d+(?:\.\d+)?)\s*(?:mg/dl|mmol/l)?",
            "Blood Pressure": r"(?i)\b(?:blood pressure|bp)\b[^\d\n]*(\d{2,3})\s*/\s*(\d{2,3})\s*(?:mm\s*hg|mmhg)?",
            "Vitamin D3": r"(?i)\b(?:vitamin d3|vit d3|vitamin d|25-hydroxyvitamin d)\b[^\d\n]*(\d+(?:\.\d+)?)\s*(?:ng/ml)?",
            "Vitamin B12": r"(?i)\b(?:vitamin b12|vit b12|cobalamin)\b[^\d\n]*(\d{2,4}(?:,\d{3})?|\d+(?:\.\d+)?)\s*(?:pg/ml)?",
            "Thyroid TSH": r"(?i)\b(?:tsh|thyroid stimulating hormone)\b[^\d\n]*(\d+(?:\.\d+)?)\s*(?:uui/ml|uiu/ml|miu/l|uip/ml|uIU/mL)?"
        }

        for param, regex in patterns.items():
            match = re.search(regex, text)
            if match:
                if param == "Blood Pressure":
                    systolic = float(match.group(1))
                    diastolic = float(match.group(2))
                    results["Systolic Blood Pressure"] = {"value": systolic, "unit": "mmHg"}
                    results["Diastolic Blood Pressure"] = {"value": diastolic, "unit": "mmHg"}
                else:
                    val_str = match.group(1).replace(",", "")  # Handle commas
                    val = float(val_str)
                    
                    # Standardize units based on parameter
                    unit = "mg/dL"
                    if param == "Hemoglobin":
                        unit = "g/dL"
                    elif param == "RBC":
                        unit = "million/mcL"
                    elif param in ["WBC", "Platelets"]:
                        unit = "x10^3/uL"
                        # Standardize WBC and Platelet ranges
                        if param == "Platelets" and val > 1000:
                            val = val / 1000  # Convert 150,000 -> 150
                        if param == "WBC" and val > 1000:
                            val = val / 1000  # Convert 6,500 -> 6.5
                    elif param == "Vitamin D3":
                        unit = "ng/mL"
                    elif param == "Vitamin B12":
                        unit = "pg/mL"
                    elif param == "Thyroid TSH":
                        unit = "uIU/mL"
                    
                    results[param] = {"value": val, "unit": unit}

        return results

    def extract_with_spacy(self, text: str) -> dict:
        """Performs token level matching to extract parameters."""
        if not self.nlp or not self.matcher:
            return {}

        results = {}
        doc = self.nlp(text)
        matches = self.matcher(doc)

        for match_id, start, end in matches:
            string_id = self.nlp.vocab.strings[match_id]
            span = doc[start:end]
            
            # Find the value which is usually the last token (the number)
            val_token = span[-1]
            if val_token.like_num:
                try:
                    val_str = val_token.text.replace(",", "")
                    val = float(val_str)
                    
                    # Map spaCy match to parameter names
                    param_name = None
                    unit = ""
                    if string_id == "HEMOGLOBIN":
                        param_name = "Hemoglobin"
                        unit = "g/dL"
                    elif string_id == "RBC":
                        param_name = "RBC"
                        unit = "million/mcL"
                    elif string_id == "WBC":
                        param_name = "WBC"
                        unit = "x10^3/uL"
                        if val > 1000:
                            val = val / 1000
                    elif string_id == "PLATELETS":
                        param_name = "Platelets"
                        unit = "x10^3/uL"
                        if val > 1000:
                            val = val / 1000
                    elif string_id == "GLUCOSE":
                        param_name = "Blood Sugar"
                        unit = "mg/dL"
                    elif string_id == "CHOLESTEROL":
                        param_name = "Cholesterol"
                        unit = "mg/dL"
                    elif string_id == "VITAMIN_D3":
                        param_name = "Vitamin D3"
                        unit = "ng/mL"
                    elif string_id == "VITAMIN_B12":
                        param_name = "Vitamin B12"
                        unit = "pg/mL"
                    elif string_id == "TSH":
                        param_name = "Thyroid TSH"
                        unit = "uIU/mL"

                    if param_name:
                        results[param_name] = {"value": val, "unit": unit}
                except ValueError:
                    continue
        return results

    def extract_parameters(self, text: str) -> list:
        """
        Extracts and merges parameters from both spaCy and Regex methods.
        Returns a list of dicts: [{'name': '...', 'value': 12.5, 'unit': '...'}]
        """
        # Run Regex (very strong on structured medical report layouts)
        regex_results = self.extract_with_regex(text)
        
        # Run spaCy (better for token patterns)
        spacy_results = self.extract_with_spacy(text) if self.nlp else {}

        # Merge results, giving Regex precedence for structure, but combining unique matches
        merged = {}
        for k, v in spacy_results.items():
            merged[k] = v
        for k, v in regex_results.items():
            merged[k] = v  # Overwrite with regex as it is highly specific

        # Convert dictionary to formatted list
        output = []
        for param, data in merged.items():
            output.append({
                "parameter_name": param,
                "value": data["value"],
                "unit": data["unit"]
            })
            
        logger.info(f"Extracted parameters: {output}")
        return output
