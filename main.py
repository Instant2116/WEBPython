from http.client import HTTPException

from fastapi import FastAPI, Depends, Form, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

import crud
import database
import schemas
from models import User

app = FastAPI()
security = HTTPBasic()
database.init_db()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

'''
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

'''


@app.get("/", response_class=HTMLResponse)
async def login_page():
    html_content = """
    <html>
        <head><title>Login</title></head>
        <body>
            <h1>Login</h1>
            <form action="/" method="post">
                <label for="username">Username:</label>
                <input type="text" name="username" required><br>

                <label for="password">Password:</label>
                <input type="password" name="password" required><br>

                <input type="submit" value="Login">
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/", response_class=HTMLResponse)
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.role.name == "admin":
        return RedirectResponse(url="/items-found", status_code=303)
    else:
        return RedirectResponse(url="/items-lost", status_code=303)


def get_current_user(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    if credentials is None:
        guest_user = User(username="guest", password="", role_id=2)
        return guest_user

    try:
        user = db.query(User).filter(User.username == credentials.username).first()
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    if user is None or user.password != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return user


def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this resource",
        )
    return current_user


@app.get("/items-found", response_class=HTMLResponse)
async def items_found(db: Session = Depends(get_db), user: User = Depends(get_admin_user)):
    if user.role.name != "admin":
        raise HTTPException(status_code=403, detail="You do not have access to this resource")

    items = crud.get_items(db)

    html_content = """
    <html>
        <head><title>Found Items</title></head>
        <body>
            <h1>Found Items</h1>
            <ul>
    """

    for item in items:
        html_content += f"""
            <li>
                {item.id} -{item.name} - {item.description}

                <!-- Update Form -->
                <form action="/update-item/{item.id}" method="post" style="display:inline;">
                    <input type="text" name="new_name" placeholder="New Name" />
                    <input type="text" name="new_description" placeholder="New Description" />
                    <input type="submit" value="Update" />
                </form>

                <!-- Delete Form -->
                <form action="/delete-item/{item.id}" method="post" style="display:inline;">
                    <input type="submit" value="Delete" />
                </form>
            </li>
        """

    html_content += """
            </ul>
            <h2>Create a New Item</h2>
            <form action="/create-item" method="post">
                <input type="text" name="name" placeholder="Item Name" required />
                <input type="text" name="description" placeholder="Item Description" required />
                <input type="submit" value="Create Item" />
            </form>
        </body>
    </html>
    """

    return HTMLResponse(content=html_content)


@app.get("/items-lost", response_class=HTMLResponse)
async def items_lost(db: Session = Depends(get_db)):
    items = crud.get_lost_items(db)

    html_content = """
    <html>
        <head><title>Lost Items</title></head>
        <body>
            <h1>Lost Items</h1>
            <ul>
    """

    for item in items:
        html_content += f"""
            <li>
                {item.name} - {item.description}

                <!-- Update Form -->
                <form action="/update-lost-item/{item.id}" method="post" style="display:inline;">
                    <input type="text" name="new_name" placeholder="New Name" />
                    <input type="text" name="new_description" placeholder="New Description" />
                    <input type="submit" value="Update" />
                </form>

                <!-- Delete Form -->
                <form action="/delete-lost-item/{item.id}" method="post" style="display:inline;">
                    <input type="submit" value="Delete" />
                </form>
            </li>
        """

    html_content += """
            </ul>
            <h2>Create a New Item</h2>
            <form action="/create-lost-item" method="post">
                <input type="text" name="name" placeholder="Item Name" required />
                <input type="text" name="description" placeholder="Item Description" required />
                <input type="submit" value="Create Item" />
            </form>
        </body>
    </html>
    """

    return HTMLResponse(content=html_content)


@app.post("/create-item")
async def create_item(name: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    new_item = schemas.ItemCreate(name=name, description=description)
    created_item = crud.create_item(db, new_item)

    return HTMLResponse(content="<h2>Item created successfully!</h2><a href='/items-found'>Back</a>")


@app.post("/update-item/{item_id}")
async def update_item(item_id: int, new_name: str = Form(...), new_description: str = Form(...),
                      db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    updated_item = schemas.ItemCreate(name=new_name, description=new_description)
    crud.update_item(db, item_id, updated_item)

    return HTMLResponse(content="<h2>Item updated successfully!</h2><a href='/items-found'>Back</a>")


@app.post("/delete-item/{item_id}")
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.delete_item(db, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return HTMLResponse(content="<h2>Item deleted successfully!</h2><a href='/items-found'>Back</a>")


@app.post("/create-lost-item")
async def create_lost_item(name: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    new_item = schemas.ItemCreate(name=name, description=description)
    created_item = crud.create_lost_item(db, new_item)

    return HTMLResponse(content="<h2>Item created successfully!</h2><a href='/items-lost'>Back</a>")


@app.post("/update-lost-item/{item_id}")
async def update_lost_item(item_id: int, new_name: str = Form(...), new_description: str = Form(...),
                           db: Session = Depends(get_db)):
    item = crud.get_lost_item(db, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    updated_item = schemas.ItemCreate(name=new_name, description=new_description)
    crud.update_lost_item(db, item_id, updated_item)

    return HTMLResponse(content="<h2>Item updated successfully!</h2><a href='/items-lost'>Back</a>")


@app.post("/delete-lost-item/{item_id}")
async def delete_lost_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.delete_item(db, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return HTMLResponse(content="<h2>Item deleted successfully!</h2><a href='/items-lost'>Back</a>")
