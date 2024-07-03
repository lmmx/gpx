from __future__ import annotations
from pydantic import BaseModel, Field

__all__ = [
    "ItemField",
    "ItemFieldValue",
    "Item",
    "ItemCollection",
    "ProjectDetails",
    "UserProject",
    "ItemQueryData",
    "ItemQueryResponse",
]

class ItemField(BaseModel):
    name: str

class ItemFieldValue(BaseModel):
    text: str
    field: ItemField

class Item(BaseModel):
    id: str
    field_values: list[ItemFieldValue] = Field(..., alias="fieldValues")

class ItemCollection(BaseModel):
    nodes: list[Item]

class ProjectDetails(BaseModel):
    id: str
    title: str
    short_description: str | None = Field(None, alias="shortDescription")
    items: ItemCollection

class UserProject(BaseModel):
    project: ProjectDetails = Field(..., alias="projectV2")

class ItemQueryData(BaseModel):
    viewer: UserProject

class ItemQueryResponse(BaseModel):
    data: ItemQueryData
    errors: list[dict] = []
