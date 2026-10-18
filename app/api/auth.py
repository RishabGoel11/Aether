"""
Authentication and security dependencies for the Aether REST API.
"""

from __future__ import annotations

import os

from fastapi import Header, HTTPException, status


def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """
    Validate incoming request against configured AETHER_API_KEY if present.

    If AETHER_API_KEY environment variable is set, requests without matching
    X-API-Key header will be rejected with 401 Unauthorized.
    """
    configured_key = os.environ.get("AETHER_API_KEY")
    if not configured_key:
        return

    if not x_api_key or x_api_key != configured_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header.",
        )
