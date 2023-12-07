import os
import uuid
from pathlib import Path

import aiofiles
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    SAVE_AUDIO_DIR = os.path.join(BASE_DIR, f"audio_files")

    RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'localhost')
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', ' ')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', ' ')

    REDIS_URL = os.getenv('REDIS_URL', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))

    MODEL_PATH = os.getenv('MODEL_PATH', ' ')

config = Config()

async def save_file(audio_file):
    inference_id = str(uuid.uuid4())

    save_file_path = os.path.join(config.BASE_DIR, f"audio_files")

    if not os.path.exists(save_file_path):
        os.makedirs(save_file_path)

    save_file_path = os.path.join(save_file_path, f"{inference_id}.wav")

    async with aiofiles.open(save_file_path, 'wb') as out_file:
        content = await audio_file.read()
        await out_file.write(content)
        await out_file.close()

    return save_file_path