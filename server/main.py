from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
import httpx
import os
from dotenv import load_load_dotenv

load_dotenv()

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# GitHub App credentials
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")

# GitHub API endpoints
GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_URL = "https://api.github.com"


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login")
async def login_github():
    return RedirectResponse(
        f"{GITHUB_AUTH_URL}?client_id={GITHUB_CLIENT_ID}&redirect_uri={GITHUB_REDIRECT_URI}"
    )


@app.get("/callback")
async def github_callback(code: str, request: Request):
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GITHUB_TOKEN_URL,
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )

    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")
        request.session["access_token"] = access_token
        return RedirectResponse(url="/")
    else:
        raise HTTPException(status_code=400, detail="Could not retrieve access token")


@app.get("/api/projects")
async def get_projects(request: Request):
    access_token = request.session.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITHUB_API_URL}/user/projects",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.inertia-preview+json",
            },
        )

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(
            status_code=response.status_code, detail="Error fetching projects"
        )


@app.get("/api/project/{project_id}")
async def get_project_details(project_id: int, request: Request):
    access_token = request.session.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITHUB_API_URL}/projects/{project_id}/columns",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.inertia-preview+json",
            },
        )

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(
            status_code=response.status_code, detail="Error fetching project details"
        )


@app.get("/api/column/{column_id}/cards")
async def get_column_cards(column_id: int, request: Request):
    access_token = request.session.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITHUB_API_URL}/projects/columns/{column_id}/cards",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.inertia-preview+json",
            },
        )

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(
            status_code=response.status_code, detail="Error fetching column cards"
        )


@app.post("/api/column/{column_id}/cards")
async def create_card(column_id: int, request: Request):
    access_token = request.session.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    data = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{GITHUB_API_URL}/projects/columns/{column_id}/cards",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.inertia-preview+json",
            },
            json={"note": data.get("note")},
        )

    if response.status_code == 201:
        return response.json()
    else:
        raise HTTPException(
            status_code=response.status_code, detail="Error creating card"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
