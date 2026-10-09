import re
import os
from typing import Any, Dict, List, Union

SENSITIVE_PATTERNS = [
    # AWS Access Key ID
    r"(?i)(AKIA[0-9A-Z]{16})",
    # AWS Secret Access Key (approx 40 chars base64)
    r"(?i)(aws_secret_access_key\s*[:=]\s*)([A-Za-z0-9/+=]{40})",
    # Generic password / secret / token assignment
    r"(?i)((?:password|passwd|pwd|secret|jwt_secret|token|api_key|auth_token)\s*[:=]\s*[\"']?)([^\s\"';&]+)([\"']?)",
    # Bearer tokens
    r"(?i)(Bearer\s+)([A-Za-z0-9\-._~+/]+=*)",
    # PostgreSQL / DB connection URI passwords
    r"(?i)(postgres(?:ql)?://[^:]+:)([^@/]+)(@)",
]


def redact_secrets(text: str) -> str:
    """
    Redact API keys, AWS credentials, database passwords, and secrets from strings.
    """
    if not isinstance(text, str):
        return str(text)

    redacted = text

    # Redact explicit environment variable values if set
    for env_var in [
        "AWS_SECRET_ACCESS_KEY",
        "AWS_ACCESS_KEY_ID",
        "JWT_SECRET",
        "DB_PASSWORD",
        "POSTGRES_PASSWORD",
        "GEMINI_API_KEY",
    ]:
        val = os.getenv(env_var, "").strip()
        if val and len(val) >= 4:
            redacted = redacted.replace(val, "[REDACTED]")

    # Redact using regex patterns
    redacted = re.sub(
        r"(?i)(AKIA[0-9A-Z]{16})",
        "[REDACTED_AWS_KEY]",
        redacted,
    )
    redacted = re.sub(
        r"(?i)(aws_secret_access_key\s*[:=]\s*)([A-Za-z0-9/+=]{40})",
        r"\1[REDACTED_AWS_SECRET]",
        redacted,
    )
    redacted = re.sub(
        r"(?i)(postgres(?:ql)?://[^:]+:)([^@/]+)(@)",
        r"\1[REDACTED_DB_PASS]\3",
        redacted,
    )
    redacted = re.sub(
        r"(?i)((?:password|passwd|pwd|secret|jwt_secret|token|api_key|auth_token)\s*[:=]\s*[\"']?)([^\s\"';&]+)([\"']?)",
        r"\1[REDACTED]\3",
        redacted,
    )

    return redacted


def sanitize_dict_or_list(data: Union[Dict, List, Any]) -> Any:
    """Recursively redact secrets from nested dicts or lists."""
    if isinstance(data, str):
        return redact_secrets(data)
    elif isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            if any(s in k.lower() for s in ["secret", "password", "token", "key"]):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = sanitize_dict_or_list(v)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_dict_or_list(x) for x in data]
    return data
