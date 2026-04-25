from contextlib import asynccontextmanager

from database import RECORDINGS_DIR, Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from routes import lectures, transcribe


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Udhkur", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lectures.router)
app.include_router(transcribe.router)


@app.get("/api/audio/{filename}")
async def serve_audio(filename: str):
    path = RECORDINGS_DIR / filename
    if not path.exists():
        return {"error": "not found"}
    return FileResponse(path, media_type="audio/webm")
