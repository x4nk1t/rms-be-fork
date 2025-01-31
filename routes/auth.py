import random
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from db import otp_collection, users_collection
from models import Login, LoginResponse, Signup, User, ValidateOTP, ValidateOTPRequest
from utils.constants import JWT_ALGORITHM, SECRET_KEY

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"])


async def check_user_exist(email: str):
    user = await users_collection.find_one({"email": email})
    if user is not None:
        raise HTTPException(
            status_code=400, detail="User email already exists, please login"
        )


async def send_otp(email: str):
    otp = random.randint(100000, 999999)
    otp_expiration = datetime.now(UTC) + timedelta(minutes=10)

    await otp_collection.insert_one(
        {"email": email, "otp": otp, "expires": otp_expiration}
    )

    # TODO: Send email
    return otp


@router.post("/verify-otp")
async def verify_otp(data: ValidateOTPRequest) -> dict[str, str]:
    check = await otp_collection.find_one(
        {
            "email": data.email,
            "otp": data.otp,
        }
    )

    if not check:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    if check["expires"].tzinfo is None:
        check["expires"] = check["expires"].replace(tzinfo=UTC)

    # Convert to Pydantic model
    otp_entry = ValidateOTP(**check)

    current_time = datetime.now(UTC)
    if otp_entry.expires < current_time:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    await otp_collection.delete_many(
        {
            "email": data.email,
        }
    )

    users_collection.update_one({"email": data.email}, {"$set": {"verified": True}})

    return {"msg": "Email has been verified."}


@router.post("/signup")
async def signup(data: Signup) -> dict[str, str]:
    await check_user_exist(data.email)

    hashed_password = pwd_context.hash(data.password)

    await users_collection.insert_one(
        {
            "email": data.email,
            "username": data.username,
            "password": hashed_password,
            "role": "landlord",
            "verified": False,
            "created_at": datetime.now(UTC),
        }
    )

    await send_otp(data.email)

    return {"msg": "OTP sent to email for verification."}


def create_user_session(user_detail: User) -> LoginResponse:
    # return JWT token
    expire = datetime.now(UTC) + timedelta(days=7)
    data = {"sub": user_detail["email"], "exp": expire}

    encoded_jwt = jwt.encode(data, SECRET_KEY, JWT_ALGORITHM)
    return {"token": encoded_jwt, "expires": expire}


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credential_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms={JWT_ALGORITHM})
        email: str = payload.get("email")
        if email is None:
            raise credential_exception
    except JWTError:
        raise credential_exception

    user = await users_collection.find_one({"email": email})
    if not user:
        raise credential_exception

    return user


@router.post("/login")
async def login(data: Login) -> LoginResponse:
    user_detail = await users_collection.find_one({"email": data.email})

    db_password = user_detail["password"]

    hashed_password = pwd_context.verify(data.password, db_password)

    if not hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect password!")

    return create_user_session(user_detail)
