"""
Authentication Module

This module handles user authentication and authorization for the Tutor AI system.
It provides secure password hashing, JWT token management, and user verification
functionality using industry-standard security practices.

Key Features:
- Password hashing using bcrypt for secure credential storage
- JWT (JSON Web Token) based authentication with configurable expiration
- OAuth2 password bearer token scheme for API security
- Automatic token validation and user extraction from requests

Security Features:
- Bcrypt password hashing with automatic deprecation handling
- JWT tokens with configurable expiration times
- Secure token validation with proper error handling
- HTTP 401 responses for unauthorized access attempts

Dependencies:
- jose: For JWT encoding/decoding operations
- passlib: For secure password hashing
- fastapi: For OAuth2 integration and HTTP exceptions
- config: For JWT secret and algorithm configuration

Author: Tutor AI Team
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt
from passlib.context import CryptContext
from .config import JWT_SECRET, JWT_ALGORITHM

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt for secure storage.

    Args:
        password (str): Plain text password to hash.

    Returns:
        str: Bcrypt hashed password string.
    """
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a plain password against its hashed version.

    Args:
        password (str): Plain text password to verify.
        hashed (str): Bcrypt hashed password from storage.

    Returns:
        bool: True if password matches hash, False otherwise.
    """
    return pwd_context.verify(password, hashed)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with optional expiration.

    Args:
        data (dict): Payload data to encode in the token (e.g., user ID).
        expires_delta (timedelta, optional): Token expiration time.
            Defaults to 60 minutes if not provided.

    Returns:
        str: Encoded JWT token string.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=60))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Extract and validate the current user from JWT token.

    FastAPI dependency that automatically extracts the JWT token from
    the Authorization header, validates it, and returns the user payload.

    Args:
        token (str): JWT token from Authorization header (automatically provided by FastAPI).

    Returns:
        dict: Decoded JWT payload containing user information.

    Raises:
        HTTPException: 401 Unauthorized if token is invalid, expired, or missing user data.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return payload
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
