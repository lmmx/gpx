from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional, Union
from .github_emoji import replace_github_emojis


class ItemFieldCommon(BaseModel):
    name: str
    data_type: Optional[str] = Field(None, alias="dataType")

    @field_validator("name")
    @classmethod
    def emojify(cls, v: str) -> str:
        return v if not v else replace_github_emojis(v)


class ItemFieldTextValue(BaseModel):
    text: str
    field: ItemFieldCommon

    @field_validator("text")
    @classmethod
    def emojify(cls, v: str) -> str:
        return v if not v else replace_github_emojis(v)


class ItemFieldSingleSelectValue(BaseModel):
    name: str
    field: ItemFieldCommon

    @field_validator("name")
    @classmethod
    def emojify(cls, v: str) -> str:
        return replace_github_emojis(v)

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

    @field_validator("title", "short_description")
    @classmethod
    def emojify(cls, v: str) -> str:
        return v if not v else replace_github_emojis(v)



class UserProject(BaseModel):
    project: ProjectDetails = Field(..., alias="projectV2")


class ItemQueryData(BaseModel):
    viewer: UserProject


class ItemQueryResponse(BaseModel):
    data: ItemQueryData
    errors: Optional[list[dict]] = None
