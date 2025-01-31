import os

SECRET_KEY = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
