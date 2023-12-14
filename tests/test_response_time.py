import os
import sys
import time
import logging
import argparse

import httpx

if __name__ == "__main__":
    _logger = logging.getLogger(__file__)
    handler = logging.StreamHandler(sys.stdout)
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

    with open(args.audio_path, "rb") as file:
        url = f"{args.host}:{args.port}/api/audio/upload"
        files = {"audio_file": file, "type": "audio/wav"}
        # headers = {"filename": os.path.basename(args.audio_path)}
        # _logger.debug(headers)
        with httpx.Client(timeout=120) as client:
            start = time.time()
            r = client.post(url, files=files)
            end = time.time()
            _logger.info(f"Time elapsed: {end - start}s")
            _logger.info("Response: %d\n%s", r.status_code, r.json())