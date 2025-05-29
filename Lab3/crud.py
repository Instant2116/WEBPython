from typing import List, Optional

from bson import ObjectId
from fastapi import HTTPException
from pymongo.database import Database

import schemas


def _doc_to_schema(doc: dict, schema_class: type[schemas.BaseModel]):
    """
    Converts a MongoDB document to a Pydantic model, handling the '_id'
    and ensuring all required fields are present.
    """
    if not doc:
        return None

    doc['id'] = str(doc.pop('_id', None))

    for field_name in schema_class.model_fields.keys():
        if field_name not in doc:
            doc[field_name] = None

        if field_name == 'password' and schema_class == schemas.User:
            if doc.get(field_name) is None:
                doc[field_name] = ""

    return schema_class(**doc)


def _docs_to_schemas(docs: List[dict], schema_class) -> List:
    return [_doc_to_schema(doc, schema_class) for doc in docs if doc]


def create_item(db: Database, item: schemas.ItemCreate) -> schemas.Item:
    items_collection = db.items
    item_dict = item.model_dump()
    result = items_collection.insert_one(item_dict)
    new_item_doc = items_collection.find_one({"_id": result.inserted_id})
    return _doc_to_schema(new_item_doc, schemas.Item)


def get_items(db: Database, skip: int = 0, limit: int = 100) -> List[schemas.Item]:
    items_collection = db.items
    docs = list(items_collection.find().skip(skip).limit(limit))
    return _docs_to_schemas(docs, schemas.Item)


def get_item(db: Database, item_id: str) -> Optional[schemas.Item]:
    items_collection = db.items
    try:
        item_doc = items_collection.find_one({"_id": ObjectId(item_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid item ID")
    return _doc_to_schema(item_doc, schemas.Item)


def update_item(db: Database, item_id: str, item: schemas.ItemCreate) -> Optional[schemas.Item]:
    items_collection = db.items
    try:
        result = items_collection.update_one(
            {"_id": ObjectId(item_id)}, {"$set": item.model_dump()}
        )
        if result.matched_count == 0:
            return None
        updated_item_doc = items_collection.find_one({"_id": ObjectId(item_id)})
        return _doc_to_schema(updated_item_doc, schemas.Item)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid item ID")


def delete_item(db: Database, item_id: str) -> Optional[schemas.Item]:
    items_collection = db.items
    try:
        deleted_item_doc = items_collection.find_one_and_delete({"_id": ObjectId(item_id)})
        return _doc_to_schema(deleted_item_doc, schemas.Item)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid item ID")


def create_lost_item(db: Database, item: schemas.LostItemCreate) -> schemas.LostItem:
    lost_items_collection = db.lost_items
    item_dict = item.model_dump()
    result = lost_items_collection.insert_one(item_dict)
    new_item_doc = lost_items_collection.find_one({"_id": result.inserted_id})
    return _doc_to_schema(new_item_doc, schemas.LostItem)


def get_lost_items(db: Database, skip: int = 0, limit: int = 100) -> List[schemas.LostItem]:
    lost_items_collection = db.lost_items
    docs = list(lost_items_collection.find().skip(skip).limit(limit))
    return _docs_to_schemas(docs, schemas.LostItem)


def get_lost_item(db: Database, item_id: str) -> Optional[schemas.LostItem]:
    lost_items_collection = db.lost_items
    try:
        item_doc = lost_items_collection.find_one({"_id": ObjectId(item_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid item ID")
    return _doc_to_schema(item_doc, schemas.LostItem)


def update_lost_item(
        db: Database, item_id: str, item: schemas.LostItemCreate
) -> Optional[schemas.LostItem]:
    lost_items_collection = db.lost_items
    try:
        result = lost_items_collection.update_one(
            {"_id": ObjectId(item_id)}, {"$set": item.model_dump()}
        )
        if result.matched_count == 0:
            return None
        updated_item_doc = lost_items_collection.find_one({"_id": ObjectId(item_id)})
        return _doc_to_schema(updated_item_doc, schemas.LostItem)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid item ID")


def delete_lost_item(db: Database, item_id: str) -> Optional[schemas.LostItem]:
    lost_items_collection = db.lost_items
    try:
        deleted_item_doc = lost_items_collection.find_one_and_delete(
            {"_id": ObjectId(item_id)})
        return _doc_to_schema(deleted_item_doc, schemas.LostItem)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid item ID")


def create_user(db: Database, user: schemas.UserCreate) -> schemas.User:
    users_collection = db.users
    user_dict = user.model_dump()

    user_dict["password"] = user.password
    result = users_collection.insert_one(user_dict)
    new_user_doc = users_collection.find_one({"_id": result.inserted_id})
    return _doc_to_schema(new_user_doc, schemas.User)


def get_users(db: Database, skip: int = 0, limit: int = 100) -> List[schemas.User]:
    users_collection = db.users
    pipeline = [
        {
            "$lookup": {
                "from": "roles",
                "localField": "role_id",
                "foreignField": "_id",
                "as": "role",
            }
        },
        {"$unwind": {
            "path": "$role",
            "preserveNullAndEmptyArrays": True
        }},
        {"$project": {
            "_id": 1,
            "username": 1,
            "email": 1,
            "password": 1,
            "role": {
                "_id": "$role._id",
                "name": "$role.name"
            },
        }},
        {"$skip": skip},
        {"$limit": limit},
    ]
    user_docs = list(users_collection.aggregate(pipeline))
    return _docs_to_schemas(user_docs, schemas.User)


def get_user(db: Database, user_id: str) -> Optional[schemas.User]:
    users_collection = db.users
    try:
        pipeline = [
            {"$match": {"_id": ObjectId(user_id)}},
            {
                "$lookup": {
                    "from": "roles",
                    "localField": "role_id",
                    "foreignField": "_id",
                    "as": "role",
                }
            },
            {
                "$unwind": {
                    "path": "$role",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {"$project": {
                "_id": 1,
                "username": 1,
                "email": 1,
                "password": 1,
                "role": {
                    "_id": "$role._id",
                    "name": "$role.name"
                },
            }},
        ]
        user_doc = next(users_collection.aggregate(pipeline), None)

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    return _doc_to_schema(user_doc, schemas.User)


def get_user_by_username(db: Database, username: str) -> Optional[schemas.User]:
    users_collection = db.users
    pipeline = [
        {"$match": {"username": username}},
        {
            "$lookup": {
                "from": "roles",
                "localField": "role_id",
                "foreignField": "_id",
                "as": "role",
            },
        },
        {
            "$unwind": {
                "path": "$role",
                "preserveNullAndEmptyArrays": True,
            },
        },
        {
            "$project": {
                "_id": 1,
                "username": 1,
                "email": 1,
                "password": 1,
                "role": {
                    "_id": "$role._id",
                    "name": "$role.name",
                },
            },
        },
    ]
    user_doc = next(users_collection.aggregate(pipeline), None)
    return _doc_to_schema(user_doc, schemas.User)


def update_user(
        db: Database, user_id: str, user: schemas.UserCreate
) -> Optional[schemas.User]:
    users_collection = db.users
    user_dict = user.model_dump()
    del user_dict["password"]
    try:
        result = users_collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": user_dict}
        )
        if result.matched_count == 0:
            return None
        updated_user_doc = users_collection.find_one({"_id": ObjectId(user_id)})
        return _doc_to_schema(updated_user_doc, schemas.User)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID")


def delete_user(db: Database, user_id: str) -> Optional[schemas.User]:
    users_collection = db.users
    try:
        deleted_user_doc = users_collection.find_one_and_delete(
            {"_id": ObjectId(user_id)})
        return _doc_to_schema(deleted_user_doc, schemas.User)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID")


def create_role(db: Database, role: schemas.RoleCreate) -> schemas.Role:
    roles_collection = db.roles
    role_dict = role.model_dump()
    result = roles_collection.insert_one(role_dict)
    new_role_doc = roles_collection.find_one({"_id": result.inserted_id})
    return _doc_to_schema(new_role_doc, schemas.Role)


def get_roles(db: Database, skip: int = 0, limit: int = 100) -> List[schemas.Role]:
    roles_collection = db.roles
    docs = list(roles_collection.find().skip(skip).limit(limit))
    return _docs_to_schemas(docs, schemas.Role)


def get_role(db: Database, role_id: str) -> Optional[schemas.Role]:
    roles_collection = db.roles
    try:
        role_doc = roles_collection.find_one({"_id": ObjectId(role_id)})
        return _doc_to_schema(role_doc, schemas.Role)
    except Exception:
        return None


def get_role_by_name(db: Database, name: str) -> Optional[schemas.Role]:
    roles_collection = db.roles
    role_doc = roles_collection.find_one({"name": name})
    return _doc_to_schema(role_doc, schemas.Role)
