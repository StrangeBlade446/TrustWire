"""Trustwire Financial Fraud & Social Engineering Rule Taxonomy
Defines phrase patterns, categories, negation indicators, and severity heuristics.
"""

from enum import Enum
from typing import List, Dict, Any
from pydantic import BaseModel

class FraudSeverity(str, Enum):
    INFORMATIONAL = "Informational"
    CAUTION = "Caution"
    HIGH = "High"
    CRITICAL = "Critical"

class FraudCategory(str, Enum):
    CREDENTIAL_THEFT = "Credential Theft"
    URGENCY_COERCION = "Urgency & Coercion"
    PAYMENT_DIVERSION = "Payment Diversion"
    REMOTE_ACCESS = "Remote Access Extortion"
    IMPERSONATION = "Authority / Bank Impersonation"
    REFUND_KYC_TRAP = "Refund & KYC Traps"
    INVESTMENT_EXTORTION = "Investment & Blackmail Scams"

class PatternDefinition(BaseModel):
    category: FraudCategory
    weight: int
    patterns: List[str]
    description: str

# Detection Patterns
FRAUD_PATTERNS: Dict[str, PatternDefinition] = {
    "credentials": PatternDefinition(
        category=FraudCategory.CREDENTIAL_THEFT,
        weight=40,
        patterns=[
            r"\b(?:otp|one[- ]time password|verification code)\b",
            r"\b(?:upi pin|atm pin|secret pin|security pin)\b",
            r"\b(?:cvv|cvv2|card security code|card verification value)\b",
            r"\b(?:password|passcode|banking password|netbanking credentials)\b",
            r"\b(?:seed phrase|recovery phrase|private key)\b",
            r"\b(?:share (?:the|your) code|tell me the (?:code|otp|pin))\b",
            r"\b(?:read out (?:the|your) code|forward that sms)\b",
            r"\b(?:banking details|bank details|account details|account number|routing number)\b",
            r"\b(?:card number|credit card number|debit card number|expiry date)\b",
            r"\b(?:social security|ssn|aadhaar|pan card|identity number)\b",
            r"\b(?:confirm your (?:details|identity|credentials|code|pin))\b",
            r"\b(?:give me (?:the|your) (?:code|otp|pin|password|details|credentials))\b"
        ],
        description="Requests for sensitive authentication secrets, OTPs, or passwords."
    ),
    "urgency": PatternDefinition(
        category=FraudCategory.URGENCY_COERCION,
        weight=25,
        patterns=[
            r"\b(?:immediately|right now|within (?:5|10|15) minutes|hurry up)\b",
            r"\b(?:account (?:will be|is) (?:blocked|suspended|frozen|terminated|deleted))\b",
            r"\b(?:legal action|police complaint|arrest warrant|cbi|fbi|customs department)\b",
            r"\b(?:final warning|last chance|act now or pay penalty)\b",
            r"\b(?:unauthorized transaction detected|fraudulent withdrawal)\b",
            r"\b(?:don'?t hang up|stay on the (?:line|call)|do not disconnect)\b",
            r"\b(?:keep this (?:secret|confidential)|do not tell (?:anyone|your family))\b",
            r"\b(?:avoid arrest|avoid legal action|police is on the way|face charges)\b",
            r"\b(?:urgent action required|urgent matter|immediate payment)\b"
        ],
        description="High-pressure tactics claiming immediate account suspension, arrest, or secrecy."
    ),
    "payment": PatternDefinition(
        category=FraudCategory.PAYMENT_DIVERSION,
        weight=35,
        patterns=[
            r"\b(?:transfer (?:me )?(?:the |your )?money|send (?:me )?(?:the |your )?money|pay (?:me )?(?:the |your )?money|give (?:me )?(?:the |your )?money)\b",
            r"\b(?:wire (?:me )?(?:the |your )?funds|transfer (?:me )?(?:the |your )?funds|send (?:me )?(?:the |your )?cash)\b",
            r"\b(?:scan (?:this|the) qr code|scan and pay)\b",
            r"\b(?:pay via upi|google pay|phonepe|paytm)\b",
            r"\b(?:buy (?:apple|amazon|google play) gift cards?)\b",
            r"\b(?:safe account|secure government account|temporary reserve account)\b",
            r"\b(?:deposit into this account|send bitcoin|crypto wallet|deposit (?:the )?money)\b",
            r"\b(?:pay (?:the )?(?:penalty|fine|charge|fee|bail|ransom))\b",
            r"\b(?:bail money|bail bond|release money)\b",
            r"\b(?:clear (?:the )?(?:dues|penalty|charges|taxes|fees))\b",
            r"\b(?:release (?:the )?(?:funds|parcel|consignment|money))\b",
            r"\b(?:make (?:the )?payment|send (?:the )?payment)\b"
        ],
        description="Directives to transfer funds, pay penalties, scan QR codes, or send money."
    ),
    "remote_access": PatternDefinition(
        category=FraudCategory.REMOTE_ACCESS,
        weight=40,
        patterns=[
            r"\b(?:anydesk|teamviewer|quicksupport|ultraviewer|rustdesk|zoho assist)\b",
            r"\b(?:download (?:and install )?(?:this )?(?:application|app|software))\b",
            r"\b(?:share your screen|allow remote access|grant screen sharing)\b",
            r"\b(?:accept the incoming request|open the downloaded file)\b"
        ],
        description="Coercion to install remote desktop control software or share screens."
    ),
    "impersonation": PatternDefinition(
        category=FraudCategory.IMPERSONATION,
        weight=25,
        patterns=[
            r"\b(?:calling from (?:your )?bank|bank (?:manager|executive|officer|security team))\b",
            r"\b(?:police officer|cyber crime branch|tax authority|telecom department)\b",
            r"\b(?:tech support|microsoft support|apple care support)\b",
            r"\b(?:fraud prevention department|customer care desk)\b",
            r"\b(?:customs (?:officer|department|official)|customs duty|at customs)\b",
            r"\b(?:narcotics (?:control )?bureau|ncb|illegal (?:parcel|package|shipment)|drugs? (?:found|detected))\b",
            r"\b(?:(?:parcel|package|shipment) (?:has been |was )?(?:intercepted|confiscated|seized|detained|held))\b",
            r"\b(?:investigation (?:officer|agency|team)|court official)\b",
            r"\b(?:your (?:son|daughter|relative|friend) (?:is in jail|was arrested|in hospital|needs bail))\b",
            r"\b(?:arrested|in jail|in custody|face jail time)\b"
        ],
        description="Impersonation of banks, customs, police, tech support, or distressed family."
    ),
    "refund_kyc": PatternDefinition(
        category=FraudCategory.REFUND_KYC_TRAP,
        weight=30,
        patterns=[
            r"\b(?:pending refund|cashback credited|lottery winner|tax refund)\b",
            r"\b(?:kyc (?:expired|pending|verification required|update needed))\b",
            r"\b(?:click (?:on )?(?:this|the) link to (?:verify|claim|update))\b",
            r"\b(?:electricity bill unpaid|power will be disconnected)\b",
            r"\b(?:click (?:on )?(?:this |the )?link|open (?:this |the )?link|visit (?:this )?link)\b",
            r"\b(?:download (?:this |the )?attachment|open (?:the |this )?attachment)\b",
            r"\b(?:verify (?:your )?account|claim (?:your )?(?:prize|reward|bonus))\b"
        ],
        description="Lures involving fake refunds, pending rewards, urgent KYC updates, or suspicious links."
    ),
    "extortion_investment": PatternDefinition(
        category=FraudCategory.INVESTMENT_EXTORTION,
        weight=40,
        patterns=[
            r"\b(?:guaranteed returns?|double your money|double your investment)\b",
            r"\b(?:crypto investment|trading profit|passive income scheme)\b",
            r"\b(?:leak (?:your )?photos|leak (?:your )?videos?|expose you|blackmail)\b",
            r"\b(?:pay ransom|recorded you|private pictures|private video|pay or else)\b",
            r"\b(?:send money or else|send cash or else|send funds or else)\b"
        ],
        description="Blackmail, sextortion threats, or fraudulent get-rich-quick investment schemes."
    )
}

# Negation and protective context indicators
NEGATION_PATTERNS: List[str] = [
    r"\bnever (?:share|give|reveal|disclose|tell)\b",
    r"\bdo not (?:share|give|reveal|disclose|send|transfer|scan)\b",
    r"\bdon'?t (?:share|give|reveal|disclose|send|transfer|scan)\b",
    r"\b(?:bank|police|we) will never ask (?:for|you)\b",
    r"\bnot share (?:your|the) (?:otp|pin|password)\b",
    r"\bbe careful (?:not to|about)\b",
    r"\bwarning:? (?:do not|never)\b",
    r"\brefuse to (?:share|give|send)\b"
]

# Educational, journalism, and advisory context indicators
EDUCATIONAL_PATTERNS: List[str] = [
    r"\b(?:educational (?:video|purpose|content)|for educational use)\b",
    r"\b(?:how (?:upi |bank |crypto )?fraud works|scam awareness)\b",
    r"\b(?:cyber security advisory|security awareness|psa)\b",
    r"\b(?:news report|documentary on|police advisory)\b",
    r"\b(?:example of a (?:scam|fraud|phishing))\b",
    r"\b(?:in this tutorial|today we are demonstrating)\b"
]

# Standard protective recommendations
ACTION_RECOMMENDATIONS = {
    FraudCategory.CREDENTIAL_THEFT: (
        "Never share OTPs, passwords, or PINs. Legitimate banks and support teams will never "
        "ask you to speak or type your verification code over the phone."
    ),
    FraudCategory.REMOTE_ACCESS: (
        "Do not install remote-access tools (AnyDesk, TeamViewer) or grant screen-sharing permissions. "
        "Disconnect the call immediately."
    ),
    FraudCategory.PAYMENT_DIVERSION: (
        "Stop. Do not transfer funds or scan unsolicited QR codes. Never send money to a 'safe account'."
    ),
    FraudCategory.URGENCY_COERCION: (
        "High pressure and threats of account closure or arrest are hallmarks of social engineering. "
        "Take a breath, hang up, and call the official organization directly."
    ),
    FraudCategory.REFUND_KYC_TRAP: (
        "Do not click unsolicited links or attempt KYC updates via third-party callers. "
        "Log in directly to your official banking portal or visit a local branch."
    ),
    FraudCategory.IMPERSONATION: (
        "Verify caller identity independently using the verified customer service number "
        "printed on your physical payment card or official statement."
    ),
    FraudCategory.INVESTMENT_EXTORTION: (
        "Do not pay ransom or fall for guaranteed return schemes. Report extortion threats to local cybercrime authorities immediately."
    )
}
