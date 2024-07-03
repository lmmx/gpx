from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, Union


class ItemFieldCommon(BaseModel):
    name: str
    dataType: Optional[str] = None


class ItemFieldTextValue(BaseModel):
    text: str
    field: ItemFieldCommon


class ItemFieldSingleSelectValue(BaseModel):
    name: str
    field: ItemFieldCommon


class ItemFieldDateValue(BaseModel):
    date: date
    field: ItemFieldCommon


class ItemFieldEmptyValue(BaseModel):
    pass


ItemFieldValue = Union[
    ItemFieldTextValue,
    ItemFieldSingleSelectValue,
    ItemFieldDateValue,
    ItemFieldEmptyValue,
]


class ItemFieldValueNodes(BaseModel):
    nodes: list[ItemFieldValue]


class Item(BaseModel):
    id: str
    fieldValues: ItemFieldValueNodes


class ItemCollection(BaseModel):
    nodes: list[Item]


class ProjectDetails(BaseModel):
    id: str
    title: str
    shortDescription: Optional[str] = None
    items: ItemCollection


class UserProject(BaseModel):
    project: ProjectDetails = Field(..., alias="projectV2")


class ItemQueryData(BaseModel):
    viewer: UserProject


class ItemQueryResponse(BaseModel):
    data: ItemQueryData
    errors: Optional[list[dict]] = None
