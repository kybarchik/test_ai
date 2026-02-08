from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.v1.router import api_router
from app.core.exception_handlers import register_exception_handlers
from app.core.logger import setup_logging


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    setup_logging()
    application = FastAPI()
    application.include_router(api_router)
    application.mount("/static", StaticFiles(directory="app/static"), name="static")
    application.state.templates = Jinja2Templates(directory="app/templates")
    register_exception_handlers(application)
    return application


app = create_app()
