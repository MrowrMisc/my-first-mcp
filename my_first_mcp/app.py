from fastapi import FastAPI

from my_first_mcp.controllers import dog_controller


app = FastAPI()

app.include_router(dog_controller.router, prefix="/api/v1", tags=["dogs"])
