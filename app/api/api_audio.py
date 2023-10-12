from fastapi import APIRouter, Depends, UploadFile, Response

from app.services.audio_srv import AudioSrv

router = APIRouter()

@router.post("/")
async def upload_file(audio_file: UploadFile, audio_srv: AudioSrv = Depends()) -> Response:
    response = await audio_srv.process_audio(audio_file)
    return response