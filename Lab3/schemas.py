from typing import Optional, Annotated, Union

from bson import ObjectId
from pydantic import BaseModel, Field, BeforeValidator


def validate_objectid(v: Union[str, ObjectId]) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if not ObjectId.is_valid(v):
        raise ValueError("Invalid ObjectId")
    return ObjectId(v)


PyObjectId = Annotated[
    ObjectId,
    BeforeValidator(validate_objectid)
]


class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: PyObjectId = Field(alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str
    role_id: str


class User(UserBase):
    id: PyObjectId = Field(alias="_id")
    password: str
    role: Optional[Role] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: PyObjectId = Field(alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class LostItemBase(BaseModel):
    name: str
    description: Optional[str] = None


class LostItemCreate(LostItemBase):
    pass


class LostItem(LostItemBase):
    id: PyObjectId = Field(alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
