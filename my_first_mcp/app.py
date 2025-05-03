from fastapi import FastAPI

from my_first_mcp.controllers import dog_controller

app: FastAPI | None = None

def get_app() -> FastAPI:
    global app
    if app:
        return app
    app = FastAPI()
    app.title = "Dog API"
    app.description = "An API to manage dogs"
    app.include_router(dog_controller.router, prefix="/api/v1", tags=["dogs"])
    return app
