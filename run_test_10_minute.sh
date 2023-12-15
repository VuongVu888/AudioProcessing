#!/bin/bash

conda activate audio-processing

python tests/test_response_time.py -ap ~/AudioProcessing/test_file/output_10.0.wav -ho http://localhost -p 3000