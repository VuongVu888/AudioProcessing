import asyncio
import os
import re
import time
import uuid

import redis
from fastapi import UploadFile, HTTPException
import soundfile as sf
from scipy.io.wavfile import read

from app.config.utils import save_file, config
from inference_workers.rabbitmq_publisher import rabbitmq_publisher
from transcription_model.transcription_service import TranscriptionService

# transcription_srv = TranscriptionService()

redis_client = redis.Redis(host=config.REDIS_URL, port=config.REDIS_PORT)

class AudioSrv():
    async def process_audio(self, audio_file: UploadFile):
        inference_id = str(uuid.uuid4())
        save_file_path = await save_file(audio_file, inference_id)
        audio_duration = self.get_audio_duration(save_file_path)

        start = time.time()
        inference_result = self.publish_rabbitmq(save_file_path, inference_id)
        runtime = round((time.time() - start) * 1000, 1000)
        print("Inference Runtime: ", runtime)
        # inference_result = transcription_srv.inference([save_file_path])
        os.remove(save_file_path)

        return {
            "audio_duration": audio_duration,
            "text": inference_result
        }

    def publish_rabbitmq(self, file_path, inference_id):
        headers = {
            'inference_id': inference_id
        }
        rabbitmq_publisher.publish(
            msg=file_path,
            headers=headers,
        )

        check_inference_result = redis_client.exists(inference_id)
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