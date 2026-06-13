import requests
import json
import logging

logger = logging.getLogger("MedicalApp.AIService")

class AIService:
    """Generates clinical summaries using local Ollama or a local rule-based fallback system."""

    def __init__(self, ollama_url: str = "http://localhost:11434", model_name: str = "gemma2:2b"):
        self.ollama_url = ollama_url
        self.model_name = model_name

    def generate_rule_based_summary(self, parameters: list) -> str:
        """Generates a medically accurate, template-based summary when Ollama is offline."""
        logger.info("Generating summary using rule-based fallback system.")
        abnormal_statements = []
        normal_count = 0
        critical_count = 0

        for param in parameters:
            name = param.get("parameter_name")
            val = param.get("value")
            unit = param.get("unit", "")
            classification = param.get("classification", "Normal")

            if classification == "Normal":
                normal_count += 1
                continue

            statement = ""
            if classification == "Critical":
                critical_count += 1
                prefix = "CRITICAL ALERT: "
            else:
                prefix = ""

            # Define specific explanations based on parameter
            name_lower = name.lower()
            if "hemoglobin" in name_lower or name_lower == "hgb":
                if classification in ["Low", "Critical"]:
                    statement = f"{prefix}Hemoglobin level is low ({val} {unit}), which is a common indicator of anemia and decreased oxygen-carrying capacity."
                else:
                    statement = f"{prefix}Hemoglobin level is elevated ({val} {unit}), indicating possible dehydration or polycythemia."
            elif "rbc" in name_lower:
                if classification in ["Low", "Critical"]:
                    statement = f"{prefix}Red Blood Cell (RBC) count is low ({val} {unit}), matching anemia patterns."
                else:
                    statement = f"{prefix}Red Blood Cell (RBC) count is elevated ({val} {unit})."
            elif "wbc" in name_lower:
                if classification in ["High", "Critical"]:
                    statement = f"{prefix}White Blood Cell (WBC) count is high ({val} {unit}), suggesting potential infection, inflammation, or immune response."
                elif classification == "Low":
                    statement = f"{prefix}White Blood Cell (WBC) count is low ({val} {unit}), which may indicate compromised immune defense."
            elif "platelet" in name_lower or name_lower == "plt":
                if classification in ["Low", "Critical"]:
                    statement = f"{prefix}Platelet count is low ({val} {unit}), increasing the risk of bruising or bleeding."
                else:
                    statement = f"{prefix}Platelet count is elevated ({val} {unit}), which can be reactive or indicate a thrombotic risk."
            elif "blood sugar" in name_lower or "glucose" in name_lower:
                if classification in ["High", "Critical"]:
                    statement = f"{prefix}Fasting glucose (blood sugar) is high ({val} {unit}), indicating hyperglycemia. This is consistent with pre-diabetes or diabetes and requires medical monitoring."
                elif classification == "Low":
                    statement = f"{prefix}Fasting glucose is low ({val} {unit}), indicating hypoglycemia, which requires immediate glucose intake."
            elif "cholesterol" in name_lower:
                if classification in ["High", "Critical"]:
                    statement = f"{prefix}Total Cholesterol is elevated ({val} {unit}), which increases long-term cardiovascular risk factors."
            elif "systolic" in name_lower:
                if classification in ["High", "Critical"]:
                    statement = f"{prefix}Systolic blood pressure is elevated ({val} {unit}), indicating hypertension."
                elif classification == "Low":
                    statement = f"{prefix}Systolic blood pressure is low ({val} {unit})."
            elif "diastolic" in name_lower:
                if classification in ["High", "Critical"]:
                    statement = f"{prefix}Diastolic blood pressure is elevated ({val} {unit}), indicating hypertension."
                elif classification == "Low":
                    statement = f"{prefix}Diastolic blood pressure is low ({val} {unit})."

            if statement:
                abnormal_statements.append(statement)

        if not parameters:
            return "No health parameters were detected in this report to analyze."

        if normal_count == len(parameters):
            return "All extracted medical parameters (Hemoglobin, RBC, WBC, Platelets, Blood Sugar, Cholesterol, Blood Pressure) are within normal reference ranges. Maintain a healthy diet and active lifestyle."

        summary = " ".join(abnormal_statements)
        summary += " Please consult with a healthcare professional to review these laboratory findings and receive personalized clinical advice."
        return summary

    def generate_summary(self, parameters: list) -> str:
        """
        Sends extracted parameters to a local Ollama instance for clinical summarization.
        Falls back to a structured rule-based summary if Ollama is unreachable.
        """
        if not parameters:
            return "No parameters provided for analysis."

        # Load dynamic configurations
        try:
            from src.utils import get_config
            config = get_config()
            self.ollama_url = config.get("ollama_url", self.ollama_url)
            self.model_name = config.get("ollama_model", self.model_name)
        except Exception as e:
            logger.warning(f"Failed to read live config in AI service: {e}")

        # Prepare parameters list text for prompt
        param_lines = []
        for p in parameters:
            param_lines.append(
                f"- {p['parameter_name']}: {p['value']} {p.get('unit', '')} ({p.get('classification', 'Normal')})"
            )
        param_text = "\n".join(param_lines)

        prompt = (
            "You are an expert clinical AI assistant. Summarize the following lab parameters in a professional, "
            "concise, and medically accurate health summary. Highlight abnormal, high, low, or critical values. "
            "Suggest follow-up with a medical provider. Keep the summary under 120 words. Do not provide a disclaimer "
            "about not being a doctor in every sentence; write a clean final sentence suggesting professional consultation.\n\n"
            f"Parameters:\n{param_text}\n\nSummary:"
        )

        try:
            logger.info(f"Connecting to local Ollama server at: {self.ollama_url} (Model: {self.model_name})")
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 250
                }
            }
            
            # Send HTTP POST request with 6-second timeout
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=6.0
            )
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get("response", "").strip()
                if summary:
                    logger.info("Successfully generated summary via local Ollama.")
                    return summary
            
            logger.warning(f"Ollama returned status code {response.status_code}. Using fallback.")
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Ollama server is offline or unreachable: {e}. Switching to offline fallback.")
        except Exception as e:
            logger.error(f"Unexpected error when communicating with Ollama: {e}")

        # Fallback to local rule-based system
        return self.generate_rule_based_summary(parameters)
