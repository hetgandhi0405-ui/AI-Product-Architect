import os
import pytest
from backend.utils.security_redaction import redact_secrets, sanitize_dict_or_list


def test_redact_secrets_aws_keys():
    text = "Access key AKIAIOSFODNN7EXAMPLE and secret aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    redacted = redact_secrets(text)
    assert "AKIAIOSFODNN7EXAMPLE" not in redacted
    assert "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" not in redacted
    assert "[REDACTED_AWS_KEY]" in redacted
    assert "[REDACTED_AWS_SECRET]" in redacted


def test_redact_secrets_passwords_and_urls():
    text = "Database connection: postgresql://postgres:MySecretPass123@db.example.com:5432/app"
    redacted = redact_secrets(text)
    assert "MySecretPass123" not in redacted
    assert "[REDACTED_DB_PASS]" in redacted


def test_redact_secrets_env_var(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "super-secret-production-signing-key")
    text = "Log message containing super-secret-production-signing-key in the text"
    redacted = redact_secrets(text)
    assert "super-secret-production-signing-key" not in redacted
    assert "[REDACTED]" in redacted


def test_sanitize_dict_or_list():
    data = {
        "user": "admin",
        "api_key": "raw-key-12345",
        "nested": {
            "password": "p@ssword",
            "message": "connect with AKIAIOSFODNN7EXAMPLE",
        },
    }
    sanitized = sanitize_dict_or_list(data)
    assert sanitized["api_key"] == "[REDACTED]"
    assert sanitized["nested"]["password"] == "[REDACTED]"
    assert "AKIAIOSFODNN7EXAMPLE" not in sanitized["nested"]["message"]
