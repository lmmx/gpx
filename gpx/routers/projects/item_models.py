from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, Union


class ItemFieldCommon(BaseModel):
    name: str
    data_type: Optional[str] = Field(None, alias="dataType")


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
    field_values: ItemFieldValueNodes = Field(..., alias="fieldValues")


class ItemCollection(BaseModel):
    nodes: list[Item]


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
    errors: Optional[list[dict]] = None
