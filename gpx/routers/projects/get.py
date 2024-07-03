from fastapi import APIRouter, Depends, HTTPException, Request
import textwrap
from fastapi.responses import HTMLResponse
import httpx
import logging
from ...dependencies import User, get_user
from ...jinja import templates
from ...urls import GITHUB_API_URL
from .models import ProjectsQueryResponse

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__all__ = ["get_projects", "get_project_items"]

router = APIRouter()


@router.get("/projects", response_class=HTMLResponse)
async def get_projects(request: Request, user: User = Depends(get_user)):
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
    status_code = response.status_code

    if status_code != 200:
        raise HTTPException(status_code=status_code, detail="Failed to fetch projects")

    try:
        query_result = ProjectsQueryResponse.model_validate(response.json())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid response format: {str(e)}")

    if query_result.errors:
        raise HTTPException(
            status_code=400, detail=f"Query returned errors: {query_result.errors}"
        )

    projects = sorted(query_result.data.viewer.projectsV2.nodes, key=lambda x: x.number)

    if not projects:
        raise HTTPException(
            status_code=204, detail="No projects found for user"
        )
    
    return templates.TemplateResponse("components/projects_list.html", {"request": request, "projects": projects})


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
