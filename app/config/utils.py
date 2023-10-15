import os
import uuid
from pathlib import Path

import aiofiles
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    SAVE_AUDIO_DIR = os.path.join(BASE_DIR, f"audio_files")

config = Config()

async def save_file(audio_file):
    file_uuid = uuid.uuid4()
    save_file_path = os.path.join(config.BASE_DIR, f"audio_files")

    if not os.path.exists(save_file_path):
        os.makedirs(save_file_path)

    save_file_path = os.path.join(save_file_path, f"{file_uuid}.wav")

    async with aiofiles.open(save_file_path, 'wb') as out_file:
        content = await audio_file.read()
        await out_file.write(content)
        await out_file.close()

    return save_file_path