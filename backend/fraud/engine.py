"""Trustwire Context-Aware Financial Fraud & Social Engineering Rules Engine
Evaluates spoken instructions for credential theft, coercive pressure, remote access extortion,
and fraudulent payments, accounting for negation, quotation, and educational content.
"""

import re
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from backend.fraud.rules import (
    FraudSeverity,
    FraudCategory,
    FRAUD_PATTERNS,
    NEGATION_PATTERNS,
    EDUCATIONAL_PATTERNS,
    ACTION_RECOMMENDATIONS
)

class FraudRiskAssessment(BaseModel):
    is_suspicious: bool
    severity: FraudSeverity
    risk_score: float = Field(..., ge=0.0, le=1.0)
    triggering_phrases: List[str]
    detected_categories: List[str]
    explanation: str
    protective_action: str
    context_type: str
    detection_method: str = "Contextual Rules Engine v1.0"
    timestamp: float = Field(default_factory=time.time)

class FraudRulesEngine:
    """Context-aware rules engine with negation, quotation, and educational filtering."""

    def __init__(self):
        # Precompile regexes
        self.category_regexes = {}
        for cat_key, defn in FRAUD_PATTERNS.items():
            compiled = [re.compile(p, re.IGNORECASE) for p in defn.patterns]
            self.category_regexes[cat_key] = (defn, compiled)

        self.negation_regexes = [re.compile(p, re.IGNORECASE) for p in NEGATION_PATTERNS]
        self.educational_regexes = [re.compile(p, re.IGNORECASE) for p in EDUCATIONAL_PATTERNS]

    def _has_educational_context(self, text: str) -> bool:
        """Check if transcript represents a security tutorial, news report, or PSA."""
        for regex in self.educational_regexes:
            if regex.search(text):
                return True
        return False

    def _is_negated_or_warning(self, text: str, match_phrase: str) -> bool:
        """Check if a specific triggering phrase is preceded by or wrapped in a negation."""
        lower_text = text.lower()
        # Direct check with negation regexes
        for neg_reg in self.negation_regexes:
            neg_match = neg_reg.search(lower_text)
            if neg_match:
                # Check proximity between negation and matched phrase
                phrase_idx = lower_text.find(match_phrase.lower())
                neg_idx = neg_match.start()
                # If negation is within 40 characters before or nearby
                if abs(phrase_idx - neg_idx) < 50:
                    return True
        return False

    def analyze(self, text: str, timestamp: Optional[float] = None) -> FraudRiskAssessment:
        """Perform comprehensive context-aware risk analysis on the given transcript."""
        ts = timestamp or time.time()
        cleaned_text = text.strip()

        if not cleaned_text:
            return FraudRiskAssessment(
                is_suspicious=False,
                severity=FraudSeverity.INFORMATIONAL,
                risk_score=0.0,
                triggering_phrases=[],
                detected_categories=[],
                explanation="No speech or transcript text provided.",
                protective_action="None required.",
                context_type="empty",
                timestamp=ts
            )

        # 1. Check for Educational / News / Awareness Context
        is_educational = self._has_educational_context(cleaned_text)

        # 2. Match Category Patterns
        matched_categories: Dict[FraudCategory, List[str]] = {}
        total_raw_weight = 0
        all_triggers = []

        for cat_key, (defn, regex_list) in self.category_regexes.items():
            for regex in regex_list:
                match = regex.search(cleaned_text)
                if match:
                    phrase = match.group(0)
                    # Check for negation
                    if self._is_negated_or_warning(cleaned_text, phrase):
                        # Negated phrase: do not treat as an active scam instruction
                        continue

                    if defn.category not in matched_categories:
                        matched_categories[defn.category] = []
                    matched_categories[defn.category].append(phrase)
                    all_triggers.append(phrase)
                    total_raw_weight += defn.weight

        # If all matches were negated or no matches found
        if not matched_categories:
            context_type = "educational" if is_educational else "benign"
            explanation = "Educational context detected: Safe discussion of security topics." if is_educational else "Benign conversation: No fraudulent instructions detected."
            return FraudRiskAssessment(
                is_suspicious=False,
                severity=FraudSeverity.INFORMATIONAL,
                risk_score=0.05 if is_educational else 0.0,
                triggering_phrases=[],
                detected_categories=[],
                explanation=explanation,
                protective_action="Continue normal activity.",
                context_type=context_type,
                timestamp=ts
            )

        # 3. Contextual Severity & Score Calculation
        # Base score normalized from combined weights
        num_categories = len(matched_categories)
        cat_names = [c.value for c in matched_categories.keys()]
        
        # Calculate risk score (0.0 to 1.0)
        # Combination multiplier: Multiple distinct fraud vectors heavily compound risk
        score = min(1.0, (total_raw_weight / 100.0) * (1.0 + 0.3 * (num_categories - 1)))

        # Educational dampening
        if is_educational:
            score = min(score * 0.25, 0.2)
            severity = FraudSeverity.INFORMATIONAL
            explanation = f"Educational/analytical discussion mentioning: {', '.join(all_triggers)}."
            protective_action = "No threat detected; content appears educational."
            context_type = "educational"
            is_suspicious = False
        else:
            # Determine severity based on specific dangerous combinations
            has_credentials = FraudCategory.CREDENTIAL_THEFT in matched_categories
            has_remote = FraudCategory.REMOTE_ACCESS in matched_categories
            has_urgency = FraudCategory.URGENCY_COERCION in matched_categories
            has_payment = FraudCategory.PAYMENT_DIVERSION in matched_categories
            has_impersonation = FraudCategory.IMPERSONATION in matched_categories
            has_refund = FraudCategory.REFUND_KYC_TRAP in matched_categories
            has_extortion = FraudCategory.INVESTMENT_EXTORTION in matched_categories

            # Critical: Blackmail/extortion, remote access + credentials, multi-vector urgency + payment + authority
            if (has_extortion and (has_payment or has_urgency)) or (has_remote and (has_credentials or has_payment)) or (has_credentials and has_urgency and (has_payment or has_impersonation)) or (has_impersonation and has_payment and has_urgency):
                severity = FraudSeverity.CRITICAL
                score = max(score, 0.90)
                is_suspicious = True
                explanation = f"CRITICAL ALERT: High-severity deception attack involving {', '.join(cat_names)}."
            # High: Direct extortion, credential theft, remote access, payment demand + urgency, impersonation + payment
            elif has_extortion or has_credentials or has_remote or (has_payment and (has_urgency or has_impersonation)) or (has_impersonation and has_urgency):
                severity = FraudSeverity.HIGH
                score = max(score, 0.70)
                is_suspicious = True
                explanation = f"HIGH RISK: Suspicious instructions detected involving {', '.join(cat_names)}."
            # Caution: Payment mention, urgency alone, refund/KYC trap, authority impersonation
            elif has_payment or has_urgency or has_refund or has_impersonation:
                severity = FraudSeverity.CAUTION
                score = max(score, 0.50)
                is_suspicious = True
                explanation = f"CAUTION: Potential social-engineering language detected ({', '.join(cat_names)})."
            else:
                severity = FraudSeverity.INFORMATIONAL
                score = max(score, 0.20)
                is_suspicious = False
                explanation = f"Informational mention of {', '.join(cat_names)}."

            # Protective recommendation
            primary_cat = list(matched_categories.keys())[0]
            protective_action = ACTION_RECOMMENDATIONS.get(primary_cat, "Do not follow suspicious instructions. Contact your official institution directly.")
            context_type = "suspicious_instruction"

        return FraudRiskAssessment(
            is_suspicious=is_suspicious,
            severity=severity,
            risk_score=round(score, 2),
            triggering_phrases=list(set(all_triggers)),
            detected_categories=cat_names,
            explanation=explanation,
            protective_action=protective_action,
            context_type=context_type,
            timestamp=ts
        )

# Global singleton
fraud_engine = FraudRulesEngine()
