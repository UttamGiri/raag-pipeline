from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from src.utils.logger import get_logger

logger = get_logger(__name__)

class PiiPresidioService:

    def __init__(self):
        provider = NlpEngineProvider({"nlp_engine_name":"spacy",
             "models":[{"lang_code":"en","model_name":"en_core_web_lg"}]})
        nlp = provider.create_engine()

        self.analyzer = AnalyzerEngine(nlp_engine=nlp)
        self.anonymizer = AnonymizerEngine()

        self.entities = [
            "PERSON","PHONE_NUMBER","EMAIL_ADDRESS","IP_ADDRESS",
            "US_SSN","CREDIT_CARD","DATE_TIME","LOCATION",
            "MEDICAL_LICENSE","HEALTH_INSURANCE_POLICY_NUMBER",
        ]

    def redact(self, text: str):
        results = self.analyzer.analyze(text=text, entities=self.entities, language="en")
        if not results:
            return text, False
        redacted = self.anonymizer.anonymize(text=text, analyzer_results=results)
        return redacted.text, True

