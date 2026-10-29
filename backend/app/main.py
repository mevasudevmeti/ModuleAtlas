from fastapi import FastAPI

from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router


app = FastAPI(
    title="ModuleAtlas API",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(chat_router)


@app.get("/")
async def root():
    return {"message": "ModuleAtlas API"}