from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

__all__ = [
    "ItemFieldCommon",
    "ItemFieldValue",
    "ItemFieldValueNodes",
    "Item",
    "ItemCollection",
    "ProjectDetails",
    "UserProject",
    "ItemQueryData",
    "ItemQueryResponse",
]

class ItemFieldCommon(BaseModel):
    name: str

class ItemFieldValue(BaseModel):
    text: Optional[str] = None
    field: Optional[ItemFieldCommon] = None

class ItemFieldValueNodes(BaseModel):
    nodes: List[ItemFieldValue]

class Item(BaseModel):
    id: str
    field_values: ItemFieldValueNodes = Field(..., alias="fieldValues")

class ItemCollection(BaseModel):
    nodes: List[Item]

class ProjectDetails(BaseModel):
    id: str
    title: str
    short_description: Optional[str] = Field(None, alias="shortDescription")
    items: ItemCollection

class UserProject(BaseModel):
    project: ProjectDetails = Field(..., alias="projectV2")

class ItemQueryData(BaseModel):
    viewer: UserProject

class ItemQueryResponse(BaseModel):
    data: ItemQueryData
    errors: Optional[List[Dict[str, Any]]] = None
