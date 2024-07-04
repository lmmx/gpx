from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import logging
from ...dependencies import User, get_user
from ...urls import GITHUB_API_URL
from .gql import add_project_item_mutation

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__all__ = ["add_project_item"]

router = APIRouter()


@router.post("/project/{project_id}/item", response_class=HTMLResponse)
async def add_project_item(project_id: str, title: str, status: str, description: str, user: User = Depends(get_user)):
    variables = {
        "input": {
            "projectId": project_id,
            "title": title,
            "body": description,
            "fieldValues": [
                {
                    "projectV2FieldId": "Status",
                    "value": status
                }
            ]
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{GITHUB_API_URL}/graphql",
            json={"query": add_project_item_mutation, "variables": variables},
            headers={
                "Authorization": f"token {user.access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
        )

    if response.status_code != 200:
        error_detail = response.json().get('errors', [{}])[0].get('message', 'Unknown error')
        raise HTTPException(
            status_code=response.status_code, 
            detail=f"Failed to add project item: {error_detail}"
        )

    data = response.json()
    new_item = data['data']['addProjectV2ItemById']['item']
    
    # Render the new item HTML
    item_html = f"""
    <div class='bg-gray-100 p-4 rounded shadow mb-4'>
        <h4 class='font-semibold mb-2'>{new_item['title']}</h4>
        {"".join([f"<p class='mb-2'><span class='font-semibold'>{field_value['field']['name']}:</span> {field_value['text'] if 'text' in field_value else field_value['name']}</p>"
                  for field_value in new_item['fieldValues']['nodes']])}
    </div>
    """

    return item_html
