from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["https://gpx-eta.vercel.app"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_API_URL = "https://api.github.com"

class User(BaseModel):
    access_token: str

def get_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return User(**user)

@app.get("/")
async def root():
    return {"message": "Welcome to GPX Projects API"}

@app.get("/login")
async def login():
    return RedirectResponse(
        f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope=project"
    )

@app.get("/callback")
async def callback(code: str, request: Request):
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code
    }
    async with httpx.AsyncClient() as client:
        response = await client.post("https://github.com/login/oauth/access_token", params=params, headers={"Accept": "application/json"})
    
    data = response.json()
    access_token = data.get("access_token")
    
    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to obtain access token")
    
    request.session["user"] = {"access_token": access_token}
    return RedirectResponse("https://gpx-eta.vercel.app")

@app.get("/projects", response_class=HTMLResponse)
async def get_projects(user: User = Depends(get_user)):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{GITHUB_API_URL}/user/projects", headers={
            "Authorization": f"token {user.access_token}",
            "Accept": "application/vnd.github.v3+json"
        })
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch projects")
    
    projects = response.json()
    projects_html = "".join([f"<div class='bg-white shadow rounded-lg p-4 mb-4'><h3 class='text-lg font-semibold'>{project['name']}</h3><p>{project['body']}</p></div>" for project in projects])
    
    return f"""
    <div id="projects" hx-swap-oob="true">
        {projects_html}
    </div>
    """

@app.get("/project/{project_id}/items", response_class=HTMLResponse)
async def get_project_items(project_id: int, user: User = Depends(get_user)):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{GITHUB_API_URL}/projects/{project_id}/columns", headers={
            "Authorization": f"token {user.access_token}",
            "Accept": "application/vnd.github.v3+json"
        })
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch project items")
    
    columns = response.json()
    items_html = ""
    
    for column in columns:
        items_response = await client.get(column['cards_url'], headers={
            "Authorization": f"token {user.access_token}",
            "Accept": "application/vnd.github.v3+json"
        })
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
        response = await client.post(f"{GITHUB_API_URL}/projects/{project_id}/cards", 
            json={"note": note},
            headers={
                "Authorization": f"token {user.access_token}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
    
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail="Failed to add project item")
    
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
