import asyncio
import hashlib
import os
import re
import uuid

import xxhash
import redis
from fastapi import UploadFile, HTTPException
import soundfile as sf

from app.config.const import BUF_SIZE
from app.config.utils import save_file, config
from inference_workers.rabbitmq_publisher import rabbitmq_publisher

redis_client = redis.Redis(host=config.REDIS_URL, port=config.REDIS_PORT)

class AudioSrv():
    async def process_audio(self, audio_file: UploadFile):
        # Generate a unique hash as inference id for the audio file
        audio_file_byte_format = await audio_file.read()
        inference_id = xxhash.xxh64(audio_file_byte_format).hexdigest()

        save_file_path = await save_file(audio_file_byte_format, inference_id)
        audio_duration = self.get_audio_duration(save_file_path)
        inference_result = self.publish_rabbitmq(save_file_path, inference_id)
        os.remove(save_file_path)

        return {
            "audio_duration": audio_duration,
            "text": inference_result
        }

    def publish_rabbitmq(self, file_path, inference_id):
        check_inference_result = redis_client.exists(inference_id)
        if check_inference_result:
            inference_result = redis_client.get(inference_id)
            return inference_result

        headers = {
            'inference_id': inference_id
        }
        rabbitmq_publisher.publish(
            msg=file_path,
            headers=headers,
        )

        while not check_inference_result:
            try:
                check_inference_result = redis_client.exists(inference_id)
            except:
                pass
        inference_result = redis_client.get(inference_id)

        return inference_result

    def get_audio_duration(self, file_path):
        with sf.SoundFile(file_path) as audio_file:
            duration_in_seconds = len(audio_file) / audio_file.samplerate
        return duration_in_seconds

    async def disect_audio_file(self, save_file_path):
        cmd = f'sox --i "{save_file_path}" | awk \'/Sample Rate/ {{printf \"Sample Rate: %s\\n\", $4}} /Duration/ {{printf \"Duration: %s\\n\", $5}}\''
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        sample_rate, duration = 0, 0
        if stdout:
            response = stdout.decode()
            sample_rate_pattern = r"Sample Rate: (\d+)"
            duration_pattern = r"Duration: (\d+)"

            sample_rate = float(re.search(sample_rate_pattern, response).group(1))
            duration = float(re.search(duration_pattern, response).group(1))
        if stderr:
            raise HTTPException(
                status_code=500,
                detail="There has been an error when dissecting .WAV file"
            )

        return sample_rate, duration