from unittest.mock import patch, MagicMock
from src.pii.pii_presidio import PiiPresidioService

@patch("src.pii.pii_presidio.AnalyzerEngine")
@patch("src.pii.pii_presidio.AnonymizerEngine")
@patch("src.pii.pii_presidio.NlpEngineProvider")
def test_pii_redaction(mock_nlp, mock_anon, mock_analyzer):
    mock_nlp.return_value.create_engine.return_value = MagicMock()

    mock_analyzer.return_value.analyze.return_value = ["PII"]
    mock_anon.return_value.anonymize.return_value = MagicMock(text="REDACTED")

    svc = PiiPresidioService()
    text, flag = svc.redact("ssn 123-45-6789")

    assert flag is True
    assert text == "REDACTED"

"""
    Goal of This Test

    The purpose is to test your code, NOT Presidio itself.

    Specifically:

    ✔ When Presidio “detects” PII
    → your service’s redact() should return

    "REDACTED"

    True

    The test does not call spaCy, does not load Presidio models, and does not run real PII detection.
"""