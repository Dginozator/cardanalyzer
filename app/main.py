from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import router


app = FastAPI(title="Card Analyser", version="0.1.0")
app.include_router(router)
app.mount("/", StaticFiles(directory="web", html=True), name="web")
