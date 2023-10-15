import glob
import logging
import os

from fastapi import FastAPI

from app.api.api_router import router
from app.config.utils import config

logger = logging.getLogger(__file__)

def _clear_metrics(path):
    for filepath in glob.glob(path + "*.wav"):
        os.remove(filepath)

def get_application(debug: bool = False) -> FastAPI:
    _clear_metrics(path=os.path.join(config.BASE_DIR, f"audio_files"))

    application = FastAPI(
        title="Audio Processing", openapi_url=f'/openapi.json',
        docs_url='/docs', redoc_url=None,
        description='Audio Processing',
        debug=debug
    )
    application.include_router(router=router, prefix='/api')

    return application


app = get_application()
