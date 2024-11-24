import argparse
import asyncio
import logging
import os
import random
import sys
import time

import httpx

# Usage:
# python tests/test_multi_request.py -ap <audio file folder> -ho <url> -p <port>

SUCCESS_REQUEST = 0


async def send_request(file):
    global SUCCESS_REQUEST
    url = f"{args.host}:{args.port}/api/audio/upload"
    files = {"audio_file": file, "type": "audio/wav"}
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            url,
            files=files,
        )
        if r.status_code == 200:
            SUCCESS_REQUEST += 1


if __name__ == "__main__":
    _logger = logging.getLogger(__file__)
    handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler("test_multi_request.log")
    _logger.addHandler(file_handler)
    _logger.addHandler(handler)
    _logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-ap",
        "--audio-path",
        type=str,
        default="./vivos/test/waves/VIVOSDEV01/VIVOSDEV01_R003.wav",
        required=False,
    )
    parser.add_argument(
        "-ho",
        "--host",
        type=str,
        default="http://127.0.0.1",
        required=False,
    )
    parser.add_argument(
        "-p",
        "--port",
        type=str,
        default="8000",
        required=False,
    )
    args = parser.parse_args()

    file_lists = []
    for file in os.listdir(args.audio_path):
        f = os.path.join(args.audio_path, file)
        if os.path.isfile(f):
            with open(f, "rb") as f:
                data = f.read()
                file_lists.append(data)
                f.close()

    req = []
    for i in range(500):
        file_idx = random.randint(0, len(file_lists) - 1)
        req.append(send_request(file_lists[file_idx]))
    _logger.info(f"Total Request: {len(req)}")

    loop = asyncio.get_event_loop()

    start = time.time()
    group = asyncio.gather(*req)
    loop.run_until_complete(group)
    end = time.time()

    _logger.info(f"Time elapsed: {end - start}s")
    _logger.info(f"Total Success Request: {SUCCESS_REQUEST}")
