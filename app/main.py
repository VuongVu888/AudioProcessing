from fastapi import FastAPI

from app.api.api_router import router


def get_application(debug: bool = False) -> FastAPI:
    application = FastAPI(
        title="Audio Processing", openapi_url=f'/openapi.json',
        docs_url='/docs', redoc_url=None,
        description='Audio Processing',
        debug=debug
    )
    application.include_router(router=router, prefix='/api')

    return application


app = get_application()
