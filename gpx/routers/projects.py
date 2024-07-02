from fastapi import APIRouter, Depends, HTTPException
import textwrap
from fastapi.responses import HTMLResponse
import httpx
import logging
from ..dependencies import User, get_user

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__all__ = ["get_projects", "get_project_items", "add_project_item"]

GITHUB_API_URL = "https://api.github.com"

router = APIRouter()


@router.get("/projects", response_class=HTMLResponse)
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


@router.get("/project/{project_id}/items", response_class=HTMLResponse)
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


@router.post("/project/{project_id}/item", response_class=HTMLResponse)
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
