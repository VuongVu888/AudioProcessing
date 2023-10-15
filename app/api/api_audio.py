import logging

from fastapi import APIRouter, Depends, UploadFile, Response

from app.services.audio_srv import AudioSrv

logger = logging.getLogger(__file__)
router = APIRouter()

@router.post("/upload")
async def upload_file(audio_file: UploadFile, audio_srv: AudioSrv = Depends()) -> Response:
    response = await audio_srv.process_audio(audio_file)
    return response