import asyncio
import re

from fastapi import UploadFile, HTTPException

from app.config.utils import save_file


class AudioSrv():
    async def process_audio(self, audio_file: UploadFile):
        save_file_path = await save_file(audio_file)

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

        return {
            "sample_rate": sample_rate,
            "duration": duration
        }
