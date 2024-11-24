from fastapi import APIRouter

from app.api import api_audio

router = APIRouter()
router.include_router(api_audio.router, tags=["Audio"], prefix="/audio")
