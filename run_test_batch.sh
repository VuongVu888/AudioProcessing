#!/bin/bash

conda activate audio-processing

python tests/test_multi_request.py -ap /Users/vuongvu/Downloads/Archive/ -ho http://localhost -p 3000