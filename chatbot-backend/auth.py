from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

from database import users_collection
from models import UserSignup, UserLogin

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# Tool for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Tool for reading Bearer token from headers
security = HTTPBearer()

# Router — mini app just for auth
router = APIRouter()


# ── Password helpers ──────────────────────────────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── JWT helpers ───────────────────────────────────────────

def create_token(username: str) -> str:
    expiry = datetime.utcnow() + timedelta(hours=24)
    payload = {"sub": username, "exp": expiry}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ── Dependency to protect routes ──────────────────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    username = decode_token(token)
    user = await users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ── Routes ────────────────────────────────────────────────

@router.post("/signup")
async def signup(data: UserSignup):
    # Check username already exists
    existing = await users_collection.find_one({"username": data.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Never save plain password
    hashed = hash_password(data.password)

    await users_collection.insert_one({
        "username": data.username,
        "password": hashed,
        "created_at": datetime.utcnow()
    })

    return {"message": "Account created successfully"}


@router.post("/login")
async def login(data: UserLogin):
    user = await users_collection.find_one({"username": data.username})
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    if not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Wrong password")

    token = create_token(data.username)
    return {"token": token}