from __future__ import annotations
from pydantic import BaseModel, computed_field
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

    @computed_field
    @property
    def formatted_date(self) -> str:
        return self.createdAt.strftime("%Y-%m-%d")

    @computed_field
    @property
    def status_emoji(self) -> str:
        return "🔴" if self.closed else "🟢"


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
