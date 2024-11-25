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

## Performance
```bash
Audio 5’: Time elapsed 16.60710597038269s
Audio 10’:  Time elapsed 18.642625093460083s
Audio 15’: Time elapsed 25.640119075775146s
Audio 20’: Time elapsed 32.503416776657104s
```

## Lint and Format
```bash
ruff check --fix
ruff format
```
