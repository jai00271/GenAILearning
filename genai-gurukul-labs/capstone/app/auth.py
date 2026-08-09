"""Auth header stub — replace with IdP / signed service tokens in production."""

from __future__ import annotations

from fastapi import Header, HTTPException


# Dev-only default; document rotation in your deploy README when real.
API_KEY = "dev-key"


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> str:
    """Reject missing/invalid API keys. Stub: single shared secret."""
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="invalid or missing X-API-Key")
    return x_api_key
