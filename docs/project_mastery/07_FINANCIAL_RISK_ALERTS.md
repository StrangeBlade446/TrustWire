# Trustwire — Financial Scam Risk & Semantic Fraud Engine

> **Primary Source Files:** `backend/fraud/engine.py`, `backend/fraud/rules.py`  
> **Input Modality:** Natural Language Transcripts from Whisper Automatic Speech Recognition  
> **Algorithm Type:** Context-Aware Weighted Regex Taxonomy with Compounding Multipliers  

---

## 1. Threat Landscape: Voice Cloning Meets Social Engineering

Deepfakes are rarely deployed in isolation. In the real world, synthetic voice cloning (e.g., mimicking an executive, bank manager, or family member) is combined with **social engineering playbooks** designed to induce panic, urgency, or cognitive overload.

Trustwire pairs its acoustic neural detector with a real-time **Financial Scam Risk Engine** to detect the semantic intent behind suspicious speech.

```mermaid
flowchart TD
    A[Acoustic Audio Stream] --> B[Faster-Whisper INT8 Engine<br/>Local Automatic Speech Recognition]
    B -->|Transcribed Utterance Text| C[Fraud Engine<br/>backend/fraud/engine.py]
    
    subgraph ENGINE_LOGIC["Context-Aware Fraud Logic"]
        C --> D[1. Negation Window Filter<br/>Check for 'never', 'do not', 'protect']
        D -->|Non-Negated Text| E[2. 7-Category Regex Matching<br/>Accumulate Rule Weights wi]
        E --> F[3. Compounding Multiplier<br/>Multiplier = 1.0 + 0.30 * (C - 1)]
        F --> G[4. Educational Context Check<br/>Dampen by 60% if PSA / News]
    end
    
    G --> H{Final Scam Score S}
    H -->|S < 0.30| I[No Alert / Low Risk]
    H -->|0.30 <= S < 0.60| J[Medium Advisory Warning]
    H -->|0.60 <= S < 0.85| K[High Risk Financial Alert]
    H -->|S >= 0.85| L[CRITICAL SCAM ALERT<br/>Immediate Action Required]
```

---

## 2. The 7 Threat Categories & Rule Taxonomy

In `backend/fraud/rules.py`, fraudulent intent is categorized into 7 structured threat vectors. Each rule is assigned an empirical base weight $w_i \in [15, 45]$:

| Category | Typical Threat Phrases | Weight Range ($w_i$) | Rationale |
| :--- | :--- | :--- | :--- |
| **`urgent_action`** | *"transfer immediately"*, *"act right now"*, *"account will be suspended within 10 minutes"*, *"urgent wire"* | 25 – 35 | Artificial time compression prevents victims from consulting third parties. |
| **`credential_theft`** | *"one-time password"*, *"read me the OTP"*, *"verify your CVV"*, *"confirm login PIN"*, *"card expiration"* | 35 – 45 | Direct solicitation of authentication secrets; highest single-phrase risk. |
| **`financial_coercion`** | *"arrest warrant issued"*, *"customs seizing package"*, *"tax enforcement penalty"*, *"police investigation"* | 30 – 40 | Exploits fear of legal repercussions to force compliance. |
| **`authority_impersonation`** | *"calling from federal cyber cell"*, *"bank fraud department manager"*, *"headquarters director"* | 20 – 30 | Establishes synthetic credibility and bypasses normal skepticism. |
| **`unusual_payment`** | *"buy Apple/Google gift cards"*, *"send USDT to wallet"*, *"transfer to temporary safe vault account"* | 35 – 45 | Irreversible, non-recoverable payment channels. |
| **`secrecy_pressure`** | *"do not tell your branch manager"*, *"keep this confidential"*, *"line is monitored, speak to no one"* | 25 – 35 | Isolates the victim from support networks or corporate security. |
| **`lottery_prize`** | *"congratulations you won lottery"*, *"unclaimed estate inheritance"*, *"pay processing fee to release fund"* | 20 – 30 | Advance-fee scam vectors. |

---

## 3. Mathematical Risk Formulation & Multi-Vector Compounding

A simple additive score $(\sum w_i)$ suffers from severe false positives: a legitimate business call might discuss an *"urgent"* deadline and a *"wire transfer"*, producing an artificially high sum.

To solve this, Trustwire introduces a **multi-category compounding multiplier**. In social engineering attacks, true fraud almost always crosses *multiple independent vectors* (e.g., combining Authority Impersonation + Urgency + Credential Solicitation).

### The Mathematical Formulation:
$$S = \min\left(1.0, \; \left( \frac{\sum_{i \in \mathcal{M}} w_i}{100.0} \right) \cdot \left( 1.0 + 0.30 \cdot (C - 1) \right) \right)$$
where:
- $\mathcal{M}$: Set of matched non-negated rule instances.
- $w_i$: Base weight of rule $i$.
- $C = |\{\text{Category}(i) : i \in \mathcal{M}\}|$: Number of **unique categories** represented in the match set ($C \ge 1$).

### Rationale Behind the Multiplier $1.0 + 0.30 \cdot (C - 1)$:
- If all matched keywords belong to a single category ($C=1$), the multiplier is $1.0 + 0.30(0) = 1.0$ (no amplification).
- If matched keywords span 2 categories ($C=2$), the score is amplified by $+30\%$ ($1.30$).
- If matched keywords span 3 categories ($C=3$), the score is amplified by $+60\%$ ($1.60$).
- If matched keywords span 4 categories ($C=4$), the score is amplified by $+90\%$ ($1.90$).

This guarantees that multi-vector coordinated attacks rapidly escalate to Critical alerts, while benign conversations with single-topic keyword collisions remain below the alarm threshold.

---

## 4. Contextual Nuances: Negation & Educational Dampening

### A. Negation Windowing
Naive regex engines trigger false alarms on safety advice. For example:
> *"The bank will **never ask for your OTP** or password."*

Trustwire inspects a 50-character window preceding each matched keyword:
- Negation prefix regex: `r"\b(never|don't|do not|never share|should not|refuse to|protect your)\b"`
- If a negation operator precedes the target credential pattern within 50 characters, the match is discarded ($w_i = 0$).

### B. Educational & News PSA Dampening
In training videos, news podcasts, or cybersecurity webinars, speakers legitimately mention fraud terms in an educational context:
> *"In this cybersecurity awareness training, we teach you why attackers demand urgent wire transfers..."*

When educational keywords are detected in the transcript:
- Educational whitelist patterns: `r"\b(awareness|training|scam alert|psa|warning|cybersecurity|case study|simulation)\b"`
- If triggered, the final calculated score is dampened by 60%:
  $$S_{\text{dampened}} = S_{\text{calculated}} \times 0.40$$
This drops a would-be Critical alarm down to an informational Low advisory.

---

## 5. Alert Triggering & Remediation Contracts

When $S \ge 0.60$, `FraudEngine` dispatches an `AlertItem` to `AlertHub`:

```json
{
  "id": "alert-8f2c3d1a",
  "category": "scam_risk",
  "severity": "Critical",
  "title": "High-Pressure Financial Coercion Detected",
  "explanation": "Spoken audio combines urgent transfer demands with credential solicitation across 3 fraud vectors.",
  "evidence": {
    "scam_score": 0.94,
    "matched_categories": ["urgent_action", "credential_theft", "financial_coercion"],
    "matched_snippets": ["transfer money right now", "read me the one time password"]
  },
  "source": "Whisper Speech Transcription",
  "confidence_score": 0.94,
  "suggested_action": "HANG UP IMMEDIATELY. Do not provide OTPs or transfer funds. Call your bank using the phone number printed on the back of your card."
}
```
