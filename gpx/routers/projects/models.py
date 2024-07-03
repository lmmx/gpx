from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime

__all__ = [
    "Project",
    "ProjectCollection",
    "UserProjects",
    "ProjectsQueryData",
    "ProjectsQueryResponse",
]


class Project(BaseModel):
    closed: bool
    createdAt: datetime
    public: bool
    number: int
    resourcePath: str
    title: str
    url: str


class ProjectCollection(BaseModel):
    nodes: list[Project]
    totalCount: int


class UserProjects(BaseModel):
    id: str
    login: str
    name: str | None
    projectsV2: ProjectCollection


class ProjectsQueryData(BaseModel):
    viewer: UserProjects


class ProjectsQueryResponse(BaseModel):
    data: ProjectsQueryData | None = None
    errors: list[dict] = []
