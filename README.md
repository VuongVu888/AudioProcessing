# Model Inference for Audio Transcription

## Structure

- `app`: FastAPI app
- `inference_workers`: Consumer for inferencing
- `transcription_model`: NeMo Transcription Model used for audio transcription

## Requirements

```bash
python >= 3.9
Docker version 20.10.17, build 100c701
Docker Compose version v2.10.2
```

## Usage
```bash
cd AudioProcessing
conda create -n audio-processing python=3.9
conda activate audio-processing
pip install Cython
pip install -r requirements.txt
docker compose up rabbitmq redis -d
./run.sh
```