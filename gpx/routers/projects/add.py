from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import logging
from ...dependencies import User, get_user
from ...urls import GITHUB_API_URL

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__all__ = ["add_project_item"]

router = APIRouter()


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
