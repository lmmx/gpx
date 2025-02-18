from fastapi import APIRouter, HTTPException, Request
from urllib.parse import quote
from fastapi.responses import RedirectResponse, HTMLResponse
import httpx
import logging
from ..config import settings
from ..jinja import templates

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__all__ = ["router", "login", "callback"]

GITHUB_CLIENT_ID = settings.github_client_id
GITHUB_CLIENT_SECRET = settings.github_client_secret

router = APIRouter()


@router.get("/login", response_class=RedirectResponse)
async def login():
    gh_scopes = [
        "user",
        "public_repo",
        "repo",
        "repo_deployment",
        "repo:status",
        "read:repo_hook",
        "read:org",
        "read:public_key",
        "read:gpg_key",
        "read:packages",
        "read:discussion",
        "read:enterprise",
        "read:project",
    ]
    # This is the URL suffix used by the GitHub GraphQL API Explorer app:
    # params = "&scope=user%2Cpublic_repo%2Crepo%2Crepo_deployment%2Crepo%3Astatus%2Cread%3Arepo_hook%2Cread%3Aorg%2Cread%3Apublic_key%2Cread%3Agpg_key%2Cread%3Apackages%2Cread%3Adiscussion%2Cread%3Aenterprise%2Cread%3Aproject"
    scopes = quote(",".join(gh_scopes))
    url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope={scopes}"
    return url


@router.get("/callback", response_class=RedirectResponse)
async def callback(code: str, request: Request):
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            params=params,
            headers={"Accept": "application/json"},
        )

    data = response.json()
    access_token = data.get("access_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to obtain access token")

    request.session["user"] = {"access_token": access_token}
    return settings.server_url


@router.post("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    request.session.clear()
    return templates.TemplateResponse("components/login_section.html", {"request": request, "settings": settings})
