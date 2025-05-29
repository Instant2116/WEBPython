from sqlalchemy.orm import Session, joinedload
from werkzeug.security import generate_password_hash, check_password_hash

from models import User, Role, Item, LostItem

def get_password_hash(password: str) -> str:
    return generate_password_hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return check_password_hash(hashed_password, plain_password)

def get_user(db: Session, user_id: int):
    return db.query(User).options(joinedload(User.role)).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).options(joinedload(User.role)).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).options(joinedload(User.role)).offset(skip).limit(limit).all()

def create_user(db: Session, username: str, email: str, password: str, role_id: int):
    hashed_password = get_password_hash(password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role_id=role_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_data: dict):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        for key, value in user_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

def get_role(db: Session, role_id: int):
    return db.query(Role).filter(Role.id == role_id).first()

def get_role_by_name(db: Session, name: str):
    return db.query(Role).filter(Role.name == name).first()

def get_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Role).offset(skip).limit(limit).all()

def create_role(db: Session, name: str):
    db_role = Role(name=name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def update_role(db: Session, role_id: int, role_data: dict):
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if db_role:
        for key, value in role_data.items():
            setattr(db_role, key, value)
        db.commit()
        db.refresh(db_role)
    return db_role

def delete_role(db: Session, role_id: int):
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if db_role:
        db.delete(db_role)
        db.commit()
    return db_role

def get_item(db: Session, item_id: int):
    return db.query(Item).filter(Item.id == item_id).first()

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Item).offset(skip).limit(limit).all()

def create_item(db: Session, title: str, description: str):
    db_item = Item(
        title=title,
        description=description
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item(db: Session, item_id: int, item_data: dict):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item:
        for key, value in item_data.items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item

def create_lost_item(db: Session, title: str, description: str):
    db_lost_item = LostItem(
        title=title,
        description=description
    )
    db.add(db_lost_item)
    db.commit()
    db.refresh(db_lost_item)
    return db_lost_item

def get_lost_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(LostItem).offset(skip).limit(limit).all()

def get_lost_item(db: Session, item_id: int):
    return db.query(LostItem).filter(LostItem.id == item_id).first()

def update_lost_item(db: Session, item_id: int, item_data: dict):
    db_item = db.query(LostItem).filter(LostItem.id == item_id).first()
    if db_item:
        for key, value in item_data.items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item

def delete_lost_item(db: Session, item_id: int):
    db_item = db.query(LostItem).filter(LostItem.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item