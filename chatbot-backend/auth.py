from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import hashlib
import secrets

from database import users_collection
from models import UserSignup, UserLogin

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
# Tool for reading Bearer token from headers
security = HTTPBearer()

# Router — mini app just for auth
router = APIRouter()


# ── Password helpers ──────────────────────────────────────

def hash_password(password: str) -> str:
    # Use PBKDF2 with SHA256 and a random salt
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}:{hashed.hex()}"

def verify_password(plain: str, hashed: str) -> bool:
    # Handle both old bcrypt hashes and new PBKDF2 hashes
    if hashed.startswith('$2b$') or hashed.startswith('$2a$'):
        # Old bcrypt hash - try to verify with passlib if available
        try:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            return pwd_context.verify(plain, hashed)
        except:
            return False
    elif ':' in hashed:
        # New PBKDF2 hash
        try:
            salt, hash_value = hashed.split(':')
            computed_hash = hashlib.pbkdf2_hmac('sha256', plain.encode('utf-8'), salt.encode('utf-8'), 100000)
            return secrets.compare_digest(computed_hash.hex(), hash_value)
        except:
            return False
    else:
        return False


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

    # Hash the password
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