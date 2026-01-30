import os

# Session TTL (Time To Live)
SESSION_TTL_MINUTES = 30  # Auto-delete after 30 minutes

# File upload limits
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc'}

# Vector store settings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHROMA_PERSIST_DIR = "./chroma_db"
CHROMA_COLLECTION_NAME = "indian_laws"

# Risk scoring weights
RISK_WEIGHTS = {
    "legal_invalidity": 0.5,  # 50% weight
    "deviation_severity": 0.3,  # 30% weight
    "frequency_factor": 0.2    # 20% weight
}

# Risk thresholds
RISK_LEVELS = {
    "low": (0, 30),
    "medium": (30, 60),
    "high": (60, 85),
    "critical": (85, 100)
}

# Legal rule severity scores
SEVERITY_SCORES = {
    "section_27_violation": 90,  # Non-compete (void)
    "section_23_violation": 95,  # Unlawful object (void)
    "section_74_violation": 70,  # Excessive penalty
    "ip_overreach": 60,
    "unclear_terms": 40,
    "no_violation": 0
}

# Deviation thresholds (compared to fair template)
DEVIATION_THRESHOLDS = {
    "duration_months": 12,  # Fair: ≤12 months
    "penalty_percentage": 10,  # Fair: ≤10% of salary
    "notice_period_days": 30,  # Fair: 30 days
}

# LLM settings for explanation
LLM_MODEL = "gpt-3.5-turbo"  # or configure for your LLM
LLM_MAX_TOKENS = 250
LLM_TEMPERATURE = 0.3

# Clause splitting parameters
MIN_CLAUSE_LENGTH = 30  # Minimum characters for valid clause
MAX_CLAUSE_LENGTH = 2000  # Maximum characters per clause

# Indian law data file
INDIAN_LAWS_JSON = "data/indian_laws.json"
FAIR_CONTRACT_JSON = "data/fair_contract.json"

# Logging
LOG_LEVEL = "INFO"