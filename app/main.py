"""FastAPI entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api.errors import app_error_handler
from app.api.routes import router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.services.state import build_state
from app.ui.gradio_app import create_ui


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load data once at startup."""

    app.state.app_state = build_state(get_settings())
    yield


def create_app() -> FastAPI:
    """Create the FastAPI application."""

    app = FastAPI(title="Support Ticket Intelligence", lifespan=lifespan)
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(router)

    @app.get("/", include_in_schema=False)
    def root():
        return RedirectResponse("/ui")

    import gradio as gr

    # Gradio needs state at construction time, so build a lightweight copy for UI mounting.
    ui_state = build_state(get_settings())
    gr.mount_gradio_app(app, create_ui(ui_state), path="/ui")
    return app


app = create_app()
