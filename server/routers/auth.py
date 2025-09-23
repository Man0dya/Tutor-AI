from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Optional
from ..auth import verify_password, get_password_hash, create_access_token
from ..database import get_db
from ..schemas import SignupRequest, LoginRequest, UserOut
from ..config import JWT_EXPIRE_MINUTES
from pymongo.errors import DuplicateKeyError

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/signup", response_model=UserOut)
async def signup(payload: SignupRequest, db = Depends(get_db)):
    # Check if user exists
    user = await db.users.find_one({"email": payload.email})
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = get_password_hash(payload.password)
    doc = {"email": payload.email, "password": hashed, "name": payload.name}
    try:
        res = await db.users.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already registered")
    return UserOut(id=str(res.inserted_id), email=payload.email, name=payload.name)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user.get("password")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=JWT_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": str(user.get("_id")), "email": user.get("email"), "name": user.get("name")},
        expires_delta=access_token_expires,
    )
    return {"access_token": token, "token_type": "bearer"}
