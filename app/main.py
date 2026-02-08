from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.v1.router import api_router
from app.core.logger import setup_logging


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    setup_logging()
    application = FastAPI()
    application.include_router(api_router)
    application.mount("/static", StaticFiles(directory="app/static"), name="static")
    application.state.templates = Jinja2Templates(directory="app/templates")
    return application


app = create_app()
