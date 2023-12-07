import logging
import time

from fastapi import APIRouter, Depends, UploadFile, Response

from app.services.audio_srv import AudioSrv

logger = logging.getLogger(__file__)
router = APIRouter()

@router.post("/upload")
async def upload_file(audio_file: UploadFile, audio_srv: AudioSrv = Depends()) -> Response:
    start = time.time()
    response = await audio_srv.process_audio(audio_file)
    runtime = round((time.time() - start) * 1000, 1000)
    print("Runtime: ", runtime)
    return response