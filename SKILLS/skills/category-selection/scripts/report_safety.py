"""Keep credentials out of locally generated category reports and console output."""

import re
from urllib.parse import quote, quote_plus


_SENSITIVE_FIELD = re.compile(
    r"(?:password|passwd|secret|credential|authorization|token|api[_-]?key|client[_-]?key)",
    re.IGNORECASE,
)
_SECRET_QUERY = re.compile(
    r"([?&](?:key|api_key|token|access_token|password|secret)=)[^&#\s]+",
    re.IGNORECASE,
)
REDACTED = "[REDACTED]"


def _find_secrets(value):
    """Collect credential values so copies in ordinary fields are also removed."""
    secrets = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if _SENSITIVE_FIELD.search(str(key)) and isinstance(item, str) and len(item) >= 4:
                secrets.add(item)
            else:
                secrets.update(_find_secrets(item))
    elif isinstance(value, (list, tuple)):
        for item in value:
            secrets.update(_find_secrets(item))
    return secrets


def _redact(value, secrets):
    if isinstance(value, dict):
        return {
            key: REDACTED if _SENSITIVE_FIELD.search(str(key)) else _redact(item, secrets)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_redact(item, secrets) for item in value]
    if isinstance(value, str):
        clean = _SECRET_QUERY.sub(lambda match: match.group(1) + REDACTED, value)
        for secret in sorted(secrets, key=len, reverse=True):
            clean = clean.replace(secret, REDACTED)
        return clean
    return value


def redact_report_data(value, api_key=None):
    """Return a copy with credential fields and known key values removed."""
    secrets = _find_secrets(value)
    if api_key:
        secrets.update({api_key, quote(api_key, safe=""), quote_plus(api_key)})
    return _redact(value, {secret for secret in secrets if secret})
