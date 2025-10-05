"""
Authentication Router Module

This module provides authentication endpoints for the Tutor AI system, including user registration,
login, profile management, and JWT token handling. It implements secure user authentication
with password hashing, token-based sessions, and user profile updates.

Key Features:
- User registration with email validation and duplicate checking
- Secure login with JWT token generation
- User profile retrieval and updates
- Password change functionality with current password verification
- Automatic name extraction from email for legacy accounts

Security Considerations:
- Passwords are hashed using secure hashing algorithms
- JWT tokens have configurable expiration times
- Email uniqueness is enforced across all users
- Current password verification required for password changes

Dependencies:
- FastAPI for API routing and dependency injection
- MongoDB for user data persistence
- JWT for token-based authentication
- Pydantic for request/response validation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Optional
from bson import ObjectId
from ..auth import verify_password, get_password_hash, create_access_token, get_current_user
from ..database import get_db
from ..schemas import SignupRequest, LoginRequest, UserOut, ProfileUpdateRequest
from ..config import JWT_EXPIRE_MINUTES
from pymongo.errors import DuplicateKeyError

# Create router with authentication prefix and tags for API documentation
router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth2 password bearer scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/signup", response_model=UserOut)
async def signup(payload: SignupRequest, db = Depends(get_db)):
    """
    Register a new user account.

    This endpoint creates a new user account with the provided email, password, and name.
    It performs email uniqueness validation and initializes the user with a free plan
    and zeroed usage counters.

    Args:
        payload (SignupRequest): User registration data containing email, password, and name
        db: MongoDB database dependency

    Returns:
        UserOut: Created user information (ID, email, name)

    Raises:
        HTTPException: 400 if email is already registered
    """
    # Check if user exists
    user = await db.users.find_one({"email": payload.email})
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password for secure storage
    hashed = get_password_hash(payload.password)

    # New users start on free plan with zeroed usage counters
    doc = {
        "email": payload.email,
        "password": hashed,
        "name": payload.name,
        "plan": "free",
        "usage": {"content": {"count": 0, "periodStart": datetime.utcnow().isoformat()}},
    }

    try:
        # Insert new user document into database
        res = await db.users.insert_one(doc)
    except DuplicateKeyError:
        # Handle race condition where user was created between check and insert
        raise HTTPException(status_code=400, detail="Email already registered")

    # Return user information (password not included for security)
    return UserOut(id=str(res.inserted_id), email=payload.email, name=payload.name)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    """
    Authenticate user and generate access token.

    This endpoint validates user credentials and returns a JWT access token for
    authenticated API access. It also handles legacy user accounts that may be
    missing name fields by extracting names from email addresses.

    Args:
        form_data (OAuth2PasswordRequestForm): Login form data with username (email) and password
        db: MongoDB database dependency

    Returns:
        dict: Access token and token type

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Find user by email (username field contains email)
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user.get("password")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Handle missing name field in older user accounts
    user_name = user.get("name")
    if not user_name:
        # Extract name from email if name is missing (legacy account handling)
        user_name = form_data.username.split("@")[0].title()
        # Update user in database with extracted name
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"name": user_name}}
        )

    # Create access token with user information and expiration
    access_token_expires = timedelta(minutes=JWT_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": str(user.get("_id")), "email": user.get("email"), "name": user_name},
        expires_delta=access_token_expires,
    )
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
async def get_current_user_profile(user=Depends(get_current_user)) -> UserOut:
    """
    Get current authenticated user's profile information.

    This endpoint returns the profile information of the currently authenticated user
    based on the JWT token provided in the Authorization header.

    Args:
        user: Current authenticated user information from JWT token

    Returns:
        UserOut: Current user's profile information (ID, email, name)
    """
    return UserOut(
        id=user.get("sub"),
        email=user.get("email"),
        name=user.get("name", "")
    )

@router.put("/profile", response_model=UserOut)
async def update_profile(
    payload: ProfileUpdateRequest,
    user=Depends(get_current_user),
    db=Depends(get_db)
) -> UserOut:
    """
    Update current user's profile information.

    This endpoint allows authenticated users to update their profile information,
    including name, email, and password. Email uniqueness is validated, and password
    changes require verification of the current password.

    Args:
        payload (ProfileUpdateRequest): Profile update data
        user: Current authenticated user information from JWT token
        db: MongoDB database dependency

    Returns:
        UserOut: Updated user profile information

    Raises:
        HTTPException: 404 if user not found, 400 if email taken or password validation fails
    """
    user_id = user.get("sub")

    # Retrieve current user data from database
    current_user = await db.users.find_one({"_id": ObjectId(user_id)})

    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if email is being changed and if it's already taken by another user
    if payload.email != current_user.get("email"):
        existing_user = await db.users.find_one({"email": payload.email})
        if existing_user and str(existing_user["_id"]) != user_id:
            raise HTTPException(status_code=400, detail="Email already registered")

    # Prepare update data
    update_data = {
        "name": payload.name,
        "email": payload.email
    }

    # Handle password change if provided
    if payload.new_password:
        if not payload.current_password:
            raise HTTPException(status_code=400, detail="Current password is required to set new password")

        # Verify current password before allowing change
        if not verify_password(payload.current_password, current_user.get("password")):
            raise HTTPException(status_code=400, detail="Current password is incorrect")

        # Hash and set new password
        update_data["password"] = get_password_hash(payload.new_password)

    # Update user in database
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )

    # Return updated user information
    return UserOut(
        id=user_id,
        email=payload.email,
        name=payload.name
    )
