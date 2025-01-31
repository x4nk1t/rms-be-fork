from fastapi import APIRouter, Depends

from routes import auth

router = APIRouter()


@router.get("/")
async def dashboard(current_user=Depends(auth.get_current_user)):
    return current_user
