from logging import getLogger

from fastapi import FastAPI
from uvicorn import run

from app.api.v1.documents import router
from app.core.config.default import DefaultSettings
from app.core.config.utils import get_settings, get_hostname

from app.infrastructure.vector_db.qdrant.docs_repository import QdrantFilesRepository
from app.infrastructure.persistence.postgres.connection.session import init_models_sync

logger = getLogger(__name__)


def bind_routes(application: FastAPI, setting: DefaultSettings) -> None:
    """
    Bind all routes to application.
    """
    application.include_router(router)
    # for route in list_of_routes:
    #     application.include_router(route, prefix=setting.PATH_PREFIX)


def get_app() -> FastAPI:
    """
    Creates application and all dependable objects.
    """
    description = "ExamApp API"

    tags_metadata = [
        {
            "name": "Health check",
            "description": "API health check.",
        },
    ]

    settings = get_settings()


    application = FastAPI(
        title="ExamApp",
        description=description,
        docs_url="/swagger",
        openapi_url="/openapi",
        version="1.0.0",
        openapi_tags=tags_metadata,
    )

    bind_routes(application, settings)
    application.state.settings = settings

    return application


app = get_app()

if __name__ == "__main__":
    repo = QdrantFilesRepository()
    # repo.init_storage()
    init_models_sync()

    settings_for_application = get_settings()
    run(
        "app.main:app",
        host=get_hostname(settings_for_application.APP_HOST),
        port=settings_for_application.APP_PORT,
        reload=True,
        reload_dirs=["app", "tests"],
        log_level="debug",
    )
