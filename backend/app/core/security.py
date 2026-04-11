"""
PredictIQ Security Module
JWT verification and user extraction from Supabase tokens.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
from app.core.config import settings

security = HTTPBearer()


class CurrentUser(BaseModel):
    """Represents the authenticated user from JWT."""
    id: str
    email: Optional[str] = None
    role: str = "authenticated"


def verify_jwt(token: str) -> dict:
    """Verify a Supabase JWT token and return its payload."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
            options={"verify_aud": False}
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """FastAPI dependency to extract the current user from JWT."""
    payload = verify_jwt(credentials.credentials)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID",
        )

    return CurrentUser(
        id=user_id,
        email=payload.get("email"),
        role=payload.get("role", "authenticated"),
    )
