from typing import List, Union

from fastapi import FastAPI, Depends, Form, status, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic
from pymongo.database import Database
from starlette.responses import RedirectResponse

import crud
import schemas
from database import connect_to_mongo, close_mongo_connection, get_database

app = FastAPI()
security = HTTPBasic()


@app.on_event("startup")
async def startup_event():
    connect_to_mongo()
    print("MongoDB connection established on startup.")
    db = next(get_database())
    if not crud.get_role_by_name(db, "admin"):
        crud.create_role(db, schemas.RoleCreate(name="admin"))
        print("Default 'admin' role created.")
    if not crud.get_role_by_name(db, "user"):
        crud.create_role(db, schemas.RoleCreate(name="user"))
        print("Default 'user' role created.")


@app.on_event("shutdown")
async def shutdown_event():
    close_mongo_connection()
    print("MongoDB connection closed on shutdown.")


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

                <button type="submit">Log in</button>
            </form>
            <a href="/register">Register</a>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/", response_class=HTMLResponse)
async def login_user(
        username: str = Form(...),
        password: str = Form(...),
        db: Database = Depends(get_database),
):
    user = crud.get_user_by_username(db, username)
    if not user or user.password != password:
        return HTMLResponse(
            content="""
        <html>
            <head><title>Login Failed</title></head>
            <body>
                <h1>Login Failed</h1>
                <p>Incorrect username or password.</p>
                <a href="/">Back to Login</a>
            </body>
        </html>
        """,
            status_code=401,
        )

    if user.role and user.role.name == "admin":
        response = RedirectResponse(url="/items-found", status_code=status.HTTP_302_FOUND)
    elif user.role and user.role.name == "user":
        response = RedirectResponse(url="/items-lost", status_code=status.HTTP_302_FOUND)
    else:

        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    return response


@app.get("/register", response_class=HTMLResponse)
async def register_page():
    html_content = """
    <html>
        <head><title>Register</title></head>
        <body>
            <h1>Register</h1>
            <form action="/register" method="post">
                <label for="username">Username:</label>
                <input type="text" name="username" required><br>
                <label for="email">Email:</label>
                <input type="email" name="email" required><br>
                <label for="password">Password:</label>
                <input type="password" name="password" required><br>
                <button type="submit">Register</button>
            </form>
            <a href="/">Login</a>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/register", response_class=HTMLResponse)
async def register_user(
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        db: Database = Depends(get_database),
):
    existing_user = crud.get_user_by_username(db, username)
    if existing_user:
        return HTMLResponse(
            content="""
            <html>
                <head><title>Registration Failed</title></head>
                <body>
                    <h1>Registration Failed</h1>
                    <p>Username already taken.</p>
                    <a href="/register">Back to Register</a>
                </body>
            </html>
            """,
            status_code=400,
        )

    user_role = crud.get_role_by_name(db, "user")
    if not user_role:
        return HTMLResponse(
            content="""
            <html>
                <head><title>Registration Failed</title></head>
                <body>
                    <h1>Registration Failed</h1>
                    <p>Default role 'user' not found. Please contact an administrator.</p>
                    <a href="/register">Back to Register</a>
                </body>
            </html>
            """,
            status_code=500,
        )

    user_create = schemas.UserCreate(
        username=username, email=email, password=password, role_id=str(user_role.id)
    )
    created_user = crud.create_user(db, user_create)
    return HTMLResponse(
        content="""
        <html>
            <head><title>Registration Successful</title></head>
            <body>
                <h1>Registration Successful</h1>
                <p>Your account has been created. Please <a href="/">log in</a>.</p>
            </body>
        </html>
        """,
        status_code=200,
    )


def get_html_user_list(users: List[schemas.User]):
    user_list_html = "<ul>"
    for user in users:
        role_name = user.role.name if user.role else "N/A"
        user_list_html += (
            f"<li>{user.username} ({user.email}) - Role: {role_name} (<a href='/users/{user.id}'>Details</a>)</li>"
        )
    user_list_html += "</ul>"
    return user_list_html


@app.get("/users/", response_class=HTMLResponse)
async def read_users(db: Database = Depends(get_database)):
    users = crud.get_users(db)
    user_list_html = get_html_user_list(users)
    return HTMLResponse(content=f"<h1>Users</h1>{user_list_html}<a href='/'>Back to Login</a>")


@app.get("/users/{user_id}", response_class=HTMLResponse)
async def read_user(user_id: str, db: Database = Depends(get_database)):
    user = crud.get_user(db, user_id)
    if user:
        role_name = user.role.name if user.role else "N/A"
        return HTMLResponse(
            content=f"""
            <h1>User Details</h1>
            <p>ID: {user.id}</p>
            <p>Username: {user.username}</p>
            <p>Email: {user.email}</p>
            <p>Role: {role_name}</p>
            <p><a href='/users/{user.id}/edit'>Edit User</a></p>
            <form action='/users/{user.id}/delete' method='post' onsubmit='return confirm("Are you sure you want to delete this user?");'>
                <button type='submit'>Delete User</button>
            </form>
            <a href='/users/'>Back to Users</a>
            """
        )
    raise HTTPException(status_code=404, detail="User not found")


def get_edit_user_html(user: schemas.User, roles: List[schemas.Role]):
    role_options = "".join(
        [
            f"<option value='{role.name}' {'selected' if user.role and user.role.name == role.name else ''}>{role.name}</option>"
            for role in roles
        ]
    )
    return f"""
    <html>
        <head><title>Edit User</title></head>
        <body>
            <h1>Edit User: {user.username}</h1>
            <form action="/users/{user.id}/edit" method="post">
                <label for="username">Username:</label>
                <input type="text" name="username" value="{user.username}" required><br>

                <label for="email">Email:</label>
                <input type="email" name="email" value="{user.email}" required><br>

                <label for="role_name">Role:</label>
                <select name="role_name" required>
                    {role_options}
                </select><br>

                <button type="submit">Update User</button>
            </form>
            <a href="/users/{user.id}">Back to User Details</a>
        </body>
    </html>
    """


@app.get("/users/{user_id}/edit", response_class=HTMLResponse)
async def edit_user_form(user_id: str, db: Database = Depends(get_database)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    roles = crud.get_roles(db)
    return HTMLResponse(content=get_edit_user_html(user, roles))


@app.post("/users/{user_id}/edit", response_class=HTMLResponse)
async def update_user_route(
        user_id: str,
        username: str = Form(...),
        email: str = Form(...),
        role_name: str = Form(...),
        db: Database = Depends(get_database),
):
    role = crud.get_role_by_name(db, role_name)
    if not role:
        raise HTTPException(status_code=400, detail="Invalid role name provided")

    existing_user = crud.get_user(db, user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_update = schemas.UserCreate(
        username=username, email=email, password=existing_user.password, role_id=str(role.id)
    )
    updated_user = crud.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=500, detail="Failed to update user")
    return RedirectResponse(url=f"/users/{user_id}", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/users/{user_id}/delete", response_class=HTMLResponse)
async def delete_user_route(user_id: str, db: Database = Depends(get_database)):
    deleted_user = crud.delete_user(db, user_id)
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found")
    return RedirectResponse(url="/users/", status_code=status.HTTP_303_SEE_OTHER)


def get_html_item_list(items: List[schemas.Item]):
    item_list_html = "<ul>"
    for item in items:
        item_list_html += f"""
            <li>
                {item.name}: {item.description}
                <a href='/items-found/{item.id}' style='
                    display: inline-block;
                    padding: 5px 10px;
                    margin-left: 10px;
                    background-color: 
                    color: white;
                    text-align: center;
                    text-decoration: none;
                    border-radius: 4px;
                    border: none;
                    cursor: pointer;
                '>Details</a>
                <a href='/items-found/{item.id}/edit' style='
                    display: inline-block;
                    padding: 5px 10px;
                    margin-left: 5px;
                    background-color: 
                    color: white;
                    text-align: center;
                    text-decoration: none;
                    border-radius: 4px;
                    border: none;
                    cursor: pointer;
                '>Edit</a>
                <form action='/items-found/{item.id}/delete' method='post' style='display:inline; margin-left: 5px;' onsubmit='return confirm("Are you sure you want to delete this item?");'>
                    <button type='submit' style='
                        padding: 5px 10px;
                        background-color: 
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                    '>Delete</button>
                </form>
            </li>
        """
    item_list_html += "</ul>"
    return item_list_html


@app.get("/items-found", response_class=HTMLResponse)
async def read_items(db: Database = Depends(get_database)):
    items = crud.get_items(db)
    items_list_html = get_html_item_list(items)
    return HTMLResponse(
        content=f"<h1>Found Items</h1>{items_list_html}<p><a href='/create-item-form'>Add New Item</a></p><a href='/'>Back to Login</a>")


@app.get("/items-found/{item_id}", response_class=HTMLResponse)
async def read_item(item_id: str, db: Database = Depends(get_database)):
    item = crud.get_item(db, item_id)
    if item:
        return HTMLResponse(
            content=f"""
            <h1>Item Details</h1>
            <p>ID: {item.id}</p>
            <p>Name: {item.name}</p>
            <p>Description: {item.description}</p>
            <p><a href='/items-found/{item.id}/edit'>Edit Item</a></p>
            <form action='/items-found/{item.id}/delete' method='post' onsubmit='return confirm("Are you sure you want to delete this item?");'>
                <button type='submit'>Delete Item</button>
            </form>
            <a href='/items-found'>Back to Found Items</a>
            """
        )
    raise HTTPException(status_code=404, detail="Item not found")


def get_create_item_form_html(action_url: str):
    return f"""
    <html>
        <head><title>Create Item</title></head>
        <body>
            <h1>Create New Item</h1>
            <form action="{action_url}" method="post">
                <label for="name">Name:</label>
                <input type="text" name="name" required><br>

                <label for="description">Description:</label>
                <textarea name="description"></textarea><br>

                <button type="submit">Create Item</button>
            </form>
            <a href="/items-found">Back to Found Items</a>
        </body>
    </html>
    """


@app.get("/create-item-form", response_class=HTMLResponse)
async def create_item_form():
    return HTMLResponse(content=get_create_item_form_html("/create-item"))


@app.post("/create-item", response_class=HTMLResponse)
async def create_item_route(name: str = Form(...), description: str = Form(...), db: Database = Depends(get_database)):
    new_item = schemas.ItemCreate(name=name, description=description)
    created_item = crud.create_item(db, new_item)
    return RedirectResponse(url="/items-found", status_code=status.HTTP_303_SEE_OTHER)


def get_edit_item_html(item: Union[schemas.Item, schemas.LostItem], action_url: str):
    return f"""
    <html>
        <head><title>Edit Item</title></head>
        <body>
            <h1>Edit Item: {item.name}</h1>
            <form action="{action_url}" method="post">
                <label for="name">Name:</label>
                <input type="text" name="name" value="{item.name}" required><br>

                <label for="description">Description:</label>
                <textarea name="description">{item.description}</textarea><br>

                <button type="submit">Update Item</button>
            </form>
            <a href="{action_url.rsplit('/', 2)[0]}">Back to Item Details</a>
        </body>
    </html>
    """


@app.get("/items-found/{item_id}/edit", response_class=HTMLResponse)
async def edit_item_form(item_id: str, db: Database = Depends(get_database)):
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return HTMLResponse(content=get_edit_item_html(item, f"/items-found/{item_id}/edit"))


@app.post("/items-found/{item_id}/edit", response_class=HTMLResponse)
async def update_item_route(
        item_id: str,
        name: str = Form(...),
        description: str = Form(...),
        db: Database = Depends(get_database)
):
    item_update = schemas.ItemCreate(name=name, description=description)
    updated_item = crud.update_item(db, item_id, item_update)
    if not updated_item:
        raise HTTPException(status_code=500, detail="Failed to update item")
    return RedirectResponse(url="/items-found", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/items-found/{item_id}/delete", response_class=HTMLResponse)
async def delete_item_route(item_id: str, db: Database = Depends(get_database)):
    deleted_item = crud.delete_item(db, item_id)
    if not deleted_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return RedirectResponse(url="/items-found", status_code=status.HTTP_303_SEE_OTHER)


def get_html_lost_item_list(items: List[schemas.LostItem]):
    lost_item_list_html = "<ul>"
    for item in items:
        lost_item_list_html += f"""
            <li>
                {item.name}: {item.description}
                <a href='/items-lost/{item.id}' style='
                    display: inline-block;
                    padding: 5px 10px;
                    margin-left: 10px;
                    background-color: 
                    color: white;
                    text-align: center;
                    text-decoration: none;
                    border-radius: 4px;
                    border: none;
                    cursor: pointer;
                '>Details</a>
                <a href='/items-lost/{item.id}/edit' style='
                    display: inline-block;
                    padding: 5px 10px;
                    margin-left: 5px;
                    background-color: 
                    color: white;
                    text-align: center;
                    text-decoration: none;
                    border-radius: 4px;
                    border: none;
                    cursor: pointer;
                '>Edit</a>
                <form action='/items-lost/{item.id}/delete' method='post' style='display:inline; margin-left: 5px;' onsubmit='return confirm("Are you sure you want to delete this lost item?");'>
                    <button type='submit' style='
                        padding: 5px 10px;
                        background-color: 
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                    '>Delete</button>
                </form>
            </li>
        """
    lost_item_list_html += "</ul>"
    return lost_item_list_html


@app.get("/items-lost", response_class=HTMLResponse)
async def read_lost_items(db: Database = Depends(get_database)):
    lost_items = crud.get_lost_items(db)
    lost_items_list_html = get_html_lost_item_list(lost_items)
    return HTMLResponse(
        content=f"<h1>Lost Items</h1>{lost_items_list_html}<p><a href='/create-lost-item-form'>Add New Lost Item</a></p><a href='/'>Back to Login</a>")


@app.get("/items-lost/{item_id}", response_class=HTMLResponse)
async def read_lost_item(item_id: str, db: Database = Depends(get_database)):
    item = crud.get_lost_item(db, item_id)
    if item:
        return HTMLResponse(
            content=f"""
            <h1>Lost Item Details</h1>
            <p>ID: {item.id}</p>
            <p>Name: {item.name}</p>
            <p>Description: {item.description}</p>
            <p><a href='/items-lost/{item.id}/edit'>Edit Lost Item</a></p>
            <form action='/items-lost/{item.id}/delete' method='post' onsubmit='return confirm("Are you sure you want to delete this lost item?");'>
                <button type='submit'>Delete Lost Item</button>
            </form>
            <a href='/items-lost'>Back to Lost Items</a>
            """
        )
    raise HTTPException(status_code=404, detail="Lost Item not found")


@app.get("/create-lost-item-form", response_class=HTMLResponse)
async def create_lost_item_form():
    return HTMLResponse(content=get_create_item_form_html("/create-lost-item"))


@app.post("/create-lost-item", response_class=HTMLResponse)
async def create_lost_item_route(name: str = Form(...), description: str = Form(...),
                                 db: Database = Depends(get_database)):
    new_item = schemas.LostItemCreate(name=name, description=description)
    created_item = crud.create_lost_item(db, new_item)
    return RedirectResponse(url="/items-lost", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/items-lost/{item_id}/edit", response_class=HTMLResponse)
async def edit_lost_item_form(item_id: str, db: Database = Depends(get_database)):
    item = crud.get_lost_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return HTMLResponse(content=get_edit_item_html(item, f"/items-lost/{item_id}/edit"))


@app.post("/items-lost/{item_id}/edit", response_class=HTMLResponse)
async def update_lost_item_route(
        item_id: str,
        name: str = Form(...),
        description: str = Form(...),
        db: Database = Depends(get_database)
):
    lost_item_update = schemas.LostItemCreate(name=name, description=description)
    updated_item = crud.update_lost_item(db, item_id, lost_item_update)
    if not updated_item:
        raise HTTPException(status_code=500, detail="Failed to update lost item")
    return RedirectResponse(url="/items-lost", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/delete-lost-item/{item_id}", response_class=HTMLResponse)
async def delete_lost_item_route(item_id: str, db: Database = Depends(get_database)):
    deleted_item = crud.delete_lost_item(db, item_id)
    if not deleted_item:
        raise HTTPException(status_code=404, detail="Lost Item not found")
    return RedirectResponse(url="/items-lost", status_code=status.HTTP_303_SEE_OTHER)
