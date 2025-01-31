from datetime import datetime

from pydantic import BaseModel


class OTP(BaseModel):
    email: str
    otp: int


class User(BaseModel):
    id: str
    display_name: str
    email: str
    password: str
    role: str
    verified: bool


class Signup(BaseModel):
    display_name: str
    email: str
    password: str
    created_at: datetime


class Login(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    expires: datetime


class ValidateOTP(BaseModel):
    email: str
    otp: int
    expires: datetime


class ValidateOTPRequest(BaseModel):
    email: str
    otp: int
