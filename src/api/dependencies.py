"""
API dependencies for authentication and validation.
"""

from fastapi import Header, HTTPException, status

from ..core.config import get_settings


async def verify_api_key(
    x_api_key: str | None = Header(None, description="API Key for authentication"),
) -> str:
    """
    Verify API key from request headers.

    Args:
        x_api_key: API key from X-API-Key header

    Returns:
        The validated API key

    Raises:
        HTTPException: If API key is invalid or missing
    """
    settings = get_settings()

    # Skip authentication if no API key is configured (development mode)
    if not settings.api_key:
        return "development"

    # Check if API key is provided
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required. Provide X-API-Key header.",
        )

    # Validate API key
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return x_api_key


async def get_user_id(
    x_user_id: str | None = Header(None, description="User ID for task ownership"),
) -> str:
    """
    Extract user ID from request headers.

    Args:
        x_user_id: User ID from X-User-Id header

    Returns:
        The user ID (defaults to 'anonymous' if not provided)
    """
    return x_user_id or "anonymous"
