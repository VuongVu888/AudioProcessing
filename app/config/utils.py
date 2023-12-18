import hashlib
import os
import uuid
from pathlib import Path

import aiofiles
from dotenv import load_dotenv
import soundfile as sf
import numpy as np

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

async def save_file(audio_file, inference_id=None):
    if inference_id == None:
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

def split_audio_file(input_file, output_folder, chunk_duration_seconds=5):
    # Read the audio file
    data, samplerate = sf.read(input_file)
    if len(data.shape) != 1:
        data = np.mean(data, axis=1)

    # Calculate the number of samples in each chunk
    chunk_size = int(chunk_duration_seconds * samplerate)

    # Split the audio into chunks
    num_chunks = int(np.ceil(len(data) / chunk_size))

    output_files = []
    id = str(uuid.uuid4())
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, len(data))

        # Extract the chunk
        chunk = data[start_idx:end_idx]

        # Save the chunk to a new file
        output_file = f"{output_folder}/{id}_{i + 1}.wav"
        output_files.append(output_file)
        sf.write(output_file, chunk, samplerate)

    return output_files
