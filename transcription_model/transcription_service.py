import nemo.collections.asr as nemo_asr

from app.config.utils import config


class TranscriptionService():
    def __init__(self):
        self.conformer = nemo_asr.models.EncDecCTCModelBPE.restore_from(
            restore_path=config.MODEL_PATH,
        )

    def inference(self, file_paths):
        inference_result = self.conformer.transcribe(paths2audio_files=file_paths)
        # print(inference_result.shape)

        return inference_result