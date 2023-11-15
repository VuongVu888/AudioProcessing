import asyncio
import uuid
import re
from io import BytesIO

from fastapi import UploadFile, HTTPException
import pickle
from pydub import AudioSegment

from pika import BasicProperties

from app.config.const import RABBITMQ_EXCHANGE, RABBITMQ_ROUTING_KEY
from inference_workers.rabbitmq_bridge import rabbitmq_client, redis_client


class AudioSrv():
    async def process_audio(self, audio_file: UploadFile):
        audio_content = await audio_file.read()
        audio_duration = self.get_audio_duration(audio_content)
        inference_result = self.publish_rabbitmq(audio_content)

        return {
            "audio_duration": audio_duration,
            "text": inference_result
        }

    def publish_rabbitmq(self, audio_content):
        inference_id = str(uuid.uuid4())
        rabbitmq_client.basic_publish(
            exchange=RABBITMQ_EXCHANGE,
            routing_key=RABBITMQ_ROUTING_KEY,
            body=pickle.dumps(audio_content),
            properties=BasicProperties(
                headers={
                    'inference_id': inference_id
                }
            )
        )

        check_inference_result = redis_client.exists(inference_id)
        while not check_inference_result:
            try:
                check_inference_result = redis_client.exists(inference_id)
            except:
                pass
        inference_result = redis_client.get(inference_id)

        return inference_result

    def get_audio_duration(self, audio_content):
        audio = AudioSegment.from_file(BytesIO(audio_content))
        duration_in_seconds = len(audio) / 1000.0
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