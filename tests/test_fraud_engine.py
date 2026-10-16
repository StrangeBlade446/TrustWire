"""Unit Tests for Trustwire Financial Fraud & Social Engineering Rules Engine
Verifies detection accuracy, negation filtering, educational context dampening,
and severity scoring.
"""

import pytest
from backend.fraud.engine import FraudRulesEngine
from backend.fraud.rules import FraudSeverity

@pytest.fixture
def engine():
    return FraudRulesEngine()

def test_empty_and_benign_text(engine):
    # Empty
    res = engine.analyze("")
    assert not res.is_suspicious
    assert res.severity == FraudSeverity.INFORMATIONAL
    assert res.risk_score == 0.0

    # Benign normal conversation
    res = engine.analyze("Hey Bob, let's meet at 5 PM for coffee and discuss the project roadmap.")
    assert not res.is_suspicious
    assert res.severity == FraudSeverity.INFORMATIONAL
    assert res.risk_score == 0.0

def test_negated_warning_phrases(engine):
    # Legitimate security warning from bank
    res = engine.analyze("Remember, your bank will never ask you for your OTP or password.")
    assert not res.is_suspicious
    assert res.severity == FraudSeverity.INFORMATIONAL
    assert res.context_type == "benign"

    # User warning someone else
    res = engine.analyze("Do not share your PIN with anyone over the phone.")
    assert not res.is_suspicious
    assert res.severity == FraudSeverity.INFORMATIONAL

def test_educational_and_news_context(engine):
    # Educational tutorial
    text = "In this educational video, we explain how UPI fraud works and why scammers demand an urgent transfer."
    res = engine.analyze(text)
    assert not res.is_suspicious
    assert res.severity == FraudSeverity.INFORMATIONAL
    assert res.context_type == "educational"
    assert res.risk_score <= 0.2

    # News report
    text = "Police advisory: A news report reveals scammers are tricking victims into revealing verification codes."
    res = engine.analyze(text)
    assert not res.is_suspicious
    assert res.severity == FraudSeverity.INFORMATIONAL

def test_caution_single_urgency_or_kyc(engine):
    # Single urgency mention
    res = engine.analyze("Your account will be suspended if you do not update your profile.")
    assert res.is_suspicious
    assert res.severity == FraudSeverity.CAUTION
    assert res.risk_score >= 0.40

    # KYC lure
    res = engine.analyze("Dear customer, your KYC verification required immediately to continue services.")
    assert res.is_suspicious
    assert res.severity in [FraudSeverity.CAUTION, FraudSeverity.HIGH]

def test_high_severity_credential_theft(engine):
    # Direct credential theft with urgency
    text = "I am calling from your bank security team. Tell me the OTP immediately or your account will be blocked."
    res = engine.analyze(text)
    assert res.is_suspicious
    assert res.severity in [FraudSeverity.HIGH, FraudSeverity.CRITICAL]
    assert "OTP" in [p.upper() for p in res.triggering_phrases]
    assert res.risk_score >= 0.70

def test_critical_severity_remote_access_plus_credentials(engine):
    # Remote desktop coercion + credential/payment directive
    text = "Download and install AnyDesk right now so I can verify your account and share the code."
    res = engine.analyze(text)
    assert res.is_suspicious
    assert res.severity == FraudSeverity.CRITICAL
    assert res.risk_score >= 0.85
    assert any("anydesk" in p.lower() for p in res.triggering_phrases)

def test_critical_severity_authority_coercion_wire_transfer(engine):
    # High pressure law enforcement + safe account transfer
    text = "This is the police department. An arrest warrant is issued. Transfer the money to this safe account immediately."
    res = engine.analyze(text)
    assert res.is_suspicious
    assert res.severity in [FraudSeverity.HIGH, FraudSeverity.CRITICAL]
    assert res.risk_score >= 0.70
