from fastapi import FastAPI
from pathlib import Path
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv
from .routers import auth, projects
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

load_dotenv()

app = FastAPI()
app.include_router(auth.router)
app.include_router(projects.router)

# Cookie named "gpx_session_id" to be set on `https://gpx.onrender.com`
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY"),
    https_only=True,
    session_cookie="gpx_session_id",
    same_site="strict",
)

index = (Path(__file__).parent / "index.html").read_text()


@app.get("/", response_class=HTMLResponse)
async def root():
    return index


def serve():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    serve()
