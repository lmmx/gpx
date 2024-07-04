from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from .config import settings
from .jinja import templates
from .routers import auth, projects
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = FastAPI()
app.include_router(auth.router)
app.include_router(projects.router)

# Cookie named "gpx_session_id" to be set on server URL
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key,
    https_only=True,
    session_cookie="gpx_session_id",
    same_site="strict",
)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    context = {"request": request, "settings": settings}
    return templates.TemplateResponse("index.html", context)


def serve():
    import uvicorn

    uvicorn.run("gpx.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    serve()
