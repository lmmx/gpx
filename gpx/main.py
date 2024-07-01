from fastapi import FastAPI, HTTPException, Depends, Request
from pathlib import Path
import textwrap
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

load_dotenv()

app = FastAPI()

# Cookie named "gpx_session_id" to be set on `https://gpx.onrender.com`
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY"),
    https_only=True,
    session_cookie="gpx_session_id",
    same_site="strict",
)

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_API_URL = "https://api.github.com"

index = (Path(__file__).parent / "index.html").read_text()


class User(BaseModel):
    access_token: str


def get_user(request: Request):
    logger.warning(f"Request data: {request}")
    logger.warning(f"Session data: {request.session}")
    user = request.session.get("user")
    logger.warning(f"User data from session: {user}")
    if not user:
        logger.warning("User not found in session")
        raise HTTPException(status_code=401, detail="User not authenticated")
    return User(**user)


@app.get("/", response_class=HTMLResponse)
async def root():
    return index


@app.get("/login", response_class=RedirectResponse)
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
    scopes = urllib.parse.quote(",".join(gh_scopes))
    # This is the one I was using:
    # scopes = "project read:project projects_v2 read:org repo read:user user:email"
    url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope={scopes}"
    return url


@app.get("/callback", response_class=RedirectResponse)
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
    return "https://gpx.onrender.com"


@app.get("/projects", response_class=HTMLResponse)
async def get_projects(user: User = Depends(get_user)):
    query = textwrap.dedent(
        """
    query {
      viewer {
        id
        login
        name
        projectsV2(first: 100) {
          nodes {
            closed
            createdAt
            public
            number
            resourcePath
            title
            url
          }
          totalCount
        }
      }
    }
    """
    )
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{GITHUB_API_URL}/graphql",
            headers={
                "Authorization": f"token {user.access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
            json={"query": query},
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Failed to fetch projects"
        )

    results = response.json()
    errors = results.get("errors", [])
    if errors:
        raise HTTPException(
            status_code=400, detail=f"Results came back with errors: {errors}"
        )
    projects = results.get("data", {}).get("viewer", {}).get("projectsV2")
    if not projects:
        raise HTTPException(
            status_code=204, detail=f"Results came back with no content: {results}"
        )
    logger.warn(f"Got projects:\n{projects}")
    projects_html = "".join(
        [
            f"<div class='bg-white shadow rounded-lg p-4 mb-4'><h3 class='text-lg font-semibold'>{idx}: {'Project name here'}</h3><p>{str(project)}</p></div>"
            for idx, project in enumerate(projects.items())
        ]
    )

    return f"""
    <div id="projects" hx-swap-oob="true">
        {projects_html}
    </div>
    """


@app.get("/project/{project_id}/items", response_class=HTMLResponse)
async def get_project_items(project_id: int, user: User = Depends(get_user)):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITHUB_API_URL}/projects/{project_id}/columns",
            headers={
                "Authorization": f"token {user.access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Failed to fetch project items"
        )

    columns = response.json()
    items_html = ""

    for column in columns:
        items_response = await client.get(
            column["cards_url"],
            headers={
                "Authorization": f"token {user.access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
        )
        if items_response.status_code == 200:
            items = items_response.json()
            items_html += f"<div class='bg-gray-100 p-4 mb-4'><h4 class='text-md font-semibold'>{column['name']}</h4>"
            for item in items:
                items_html += f"<div class='bg-white shadow rounded p-2 mb-2'>{item['note']}</div>"
            items_html += "</div>"

    return f"""
    <div id="project-items" hx-swap-oob="true">
        {items_html}
    </div>
    """


@app.post("/project/{project_id}/item", response_class=HTMLResponse)
async def add_project_item(project_id: int, note: str, user: User = Depends(get_user)):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{GITHUB_API_URL}/projects/{project_id}/cards",
            json={"note": note},
            headers={
                "Authorization": f"token {user.access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
        )

    if response.status_code != 201:
        raise HTTPException(
            status_code=response.status_code, detail="Failed to add project item"
        )

    new_item = response.json()
    return f"""
    <div class='bg-white shadow rounded p-2 mb-2' hx-swap-oob="beforeend:#project-items">
        {new_item['note']}
    </div>
    """


def serve():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    serve()
