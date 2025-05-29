import os
import re
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, request, flash, g, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy.orm import Session

from models import User, Role, Item, LostItem
from database import SessionLocal, init_db
import crud
from forms import LoginForm, RegistrationForm, ItemForm, LostItemForm, DeleteForm, RoleForm, UserEditForm

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

with app.app_context():
    init_db()

    db_session_initial = SessionLocal()
    try:
        if not crud.get_role_by_name(db_session_initial, 'Admin'):
            crud.create_role(db_session_initial, name='Admin')
        if not crud.get_role_by_name(db_session_initial, 'User'):
            crud.create_role(db_session_initial, name='User')
    finally:
        db_session_initial.close()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    db_session = SessionLocal()
    user = crud.get_user(db_session, user_id)
    db_session.close()
    return user

@app.before_request
def before_request():
    g.db = SessionLocal()

@app.teardown_request
def teardown_request(exception=None):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = crud.get_user_by_username(g.db, form.username.data)
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return render_template('register.html', form=form)

        user_role = crud.get_role_by_name(g.db, 'User')
        if not user_role:
            flash('Default user role not found. Please contact an administrator.', 'danger')
            return render_template('register.html', form=form)

        user = crud.create_user(
            g.db,
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            role_id=user_role.id
        )
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = crud.get_user_by_username(g.db, form.username.data)
        if user and crud.verify_password(form.password.data, user.hashed_password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_obj = current_user
    return render_template('dashboard.html', user_obj=user_obj)

@app.route('/users')
@login_required
def users_list():
    if current_user.role.name != 'Admin':
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('dashboard'))
    users = crud.get_users(g.db)
    delete_form = DeleteForm()
    return render_template('users_list.html', users=users, form=delete_form)

@app.route('/users/update/<int:user_id>', methods=['GET', 'POST'])
@login_required
def update_user(user_id):
    if current_user.role.name != 'Admin':
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))

    user = crud.get_user(g.db, user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('users_list'))

    form = UserEditForm(obj=user)
    form.role_id.choices = [(r.id, r.name) for r in crud.get_roles(g.db)]

    if form.validate_on_submit():
        data_to_update = {
            'username': form.username.data,
            'email': form.email.data,
            'role_id': form.role_id.data
        }
        try:
            crud.update_user(g.db, user_id, data_to_update)
            flash(f'User "{user.username}" updated successfully!', 'success')
            return redirect(url_for('users_list'))
        except Exception as e:
            flash(f'Error updating user: {e}', 'danger')
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.role_id.data = user.role_id
    return render_template('update_user.html', form=form, user_id=user_id)

@app.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role.name != 'Admin':
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))

    form = DeleteForm()
    if form.validate_on_submit():
        user = crud.get_user(g.db, user_id)
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('users_list'))

        try:
            crud.delete_user(g.db, user_id)
            flash(f'User "{user.username}" deleted successfully!', 'success')
        except Exception as e:
            flash(f'Error deleting user: {e}', 'danger')
    else:
        flash('Invalid request.', 'danger')
    return redirect(url_for('users_list'))

@app.route('/roles')
@login_required
def roles_list():
    if current_user.role.name != 'Admin':
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('dashboard'))
    roles = crud.get_roles(g.db)
    delete_form = DeleteForm()
    return render_template('roles_list.html', roles=roles, form=delete_form)

@app.route('/roles/create', methods=['GET', 'POST'])
@login_required
def create_role():
    if current_user.role.name != 'Admin':
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))

    form = RoleForm()
    if form.validate_on_submit():
        existing_role = crud.get_role_by_name(g.db, form.name.data)
        if existing_role:
            flash('Role with this name already exists.', 'danger')
            return render_template('create_role.html', form=form)
        try:
            crud.create_role(g.db, name=form.name.data)
            flash('Role created successfully!', 'success')
            return redirect(url_for('roles_list'))
        except Exception as e:
            flash(f'Error creating role: {e}', 'danger')
    return render_template('create_role.html', form=form)

@app.route('/roles/update/<int:role_id>', methods=['GET', 'POST'])
@login_required
def update_role(role_id):
    if current_user.role.name != 'Admin':
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))

    role = crud.get_role(g.db, role_id)
    if not role:
        flash('Role not found.', 'danger')
        return redirect(url_for('roles_list'))

    form = RoleForm(obj=role)
    if form.validate_on_submit():
        try:
            crud.update_role(g.db, role_id, {'name': form.name.data})
            flash(f'Role "{role.name}" updated successfully!', 'success')
            return redirect(url_for('roles_list'))
        except Exception as e:
            flash(f'Error updating role: {e}', 'danger')
    elif request.method == 'GET':
        form.name.data = role.name
    return render_template('update_role.html', form=form, role_id=role_id)

@app.route('/roles/delete/<int:role_id>', methods=['POST'])
@login_required
def delete_role(role_id):
    if current_user.role.name != 'Admin':
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))

    form = DeleteForm()
    if form.validate_on_submit():
        role = crud.get_role(g.db, role_id)
        if not role:
            flash('Role not found.', 'danger')
            return redirect(url_for('roles_list'))

        if role.name in ['Admin', 'User']:
            flash(f'Cannot delete default role "{role.name}".', 'danger')
            return redirect(url_for('roles_list'))

        try:
            crud.delete_role(g.db, role_id)
            flash(f'Role "{role.name}" deleted successfully!', 'success')
        except Exception as e:
            flash(f'Error deleting role: {e}', 'danger')
    else:
        flash('Invalid request.', 'danger')
    return redirect(url_for('roles_list'))

@app.route('/items/found')
@login_required
def items_found_list():
    items = crud.get_items(g.db)
    delete_form = DeleteForm()
    return render_template('items_found_list.html', items=items, form=delete_form)

@app.route('/items/found/create', methods=['GET', 'POST'])
@login_required
def create_found_item():
    form = ItemForm()
    if form.validate_on_submit():
        try:
            crud.create_item(g.db, title=form.title.data, description=form.description.data)
            flash('Found item created successfully!', 'success')
            return redirect(url_for('items_found_list'))
        except Exception as e:
            flash(f'Error creating found item: {e}', 'danger')
    return render_template('create_found_item.html', form=form)

@app.route('/items/found/update/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_found_item(item_id):
    item = crud.get_item(g.db, item_id)
    if not item:
        flash('Found item not found.', 'danger')
        return redirect(url_for('items_found_list'))

    form = ItemForm(obj=item)
    if form.validate_on_submit():
        try:
            crud.update_item(g.db, item_id, {'title': form.title.data, 'description': form.description.data})
            flash(f'Found item "{item.title}" updated successfully!', 'success')
            return redirect(url_for('items_found_list'))
        except Exception as e:
            flash(f'Error updating found item: {e}', 'danger')
    elif request.method == 'GET':
        form.title.data = item.title
        form.description.data = item.description
    return render_template('update_found_item.html', form=form, item=item)

@app.route('/items/found/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_found_item(item_id):
    form = DeleteForm()
    if form.validate_on_submit():
        item = crud.get_item(g.db, item_id)
        if not item:
            flash('Found item not found.', 'danger')
            return redirect(url_for('items_found_list'))
        try:
            crud.delete_item(g.db, item_id)
            flash(f'Found item "{item.title}" deleted successfully!', 'success')
        except Exception as e:
            flash(f'Error deleting found item: {e}', 'danger')
    else:
        flash('Invalid request.', 'danger')
    return redirect(url_for('items_found_list'))

@app.route('/items/lost')
@login_required
def items_lost_list():
    items = crud.get_lost_items(g.db)
    delete_form = DeleteForm()
    return render_template('items_lost_list.html', items=items, form=delete_form)

@app.route('/items/lost/create', methods=['GET', 'POST'])
@login_required
def create_lost_item():
    form = LostItemForm()
    if form.validate_on_submit():
        try:
            crud.create_lost_item(g.db, title=form.title.data, description=form.description.data)
            flash('Lost item created successfully!', 'success')
            return redirect(url_for('items_lost_list'))
        except Exception as e:
            flash(f'Error creating lost item: {e}', 'danger')
    return render_template('create_lost_item.html', form=form)

@app.route('/items/lost/update/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_lost_item(item_id):
    item = crud.get_lost_item(g.db, item_id)
    if not item:
        flash('Lost item not found.', 'danger')
        return redirect(url_for('items_lost_list'))

    form = LostItemForm(obj=item)
    if form.validate_on_submit():
        try:
            crud.update_lost_item(g.db, item_id, {'title': form.title.data, 'description': form.description.data})
            flash(f'Lost item "{item.title}" updated successfully!', 'success')
            return redirect(url_for('items_lost_list'))
        except Exception as e:
            flash(f'Error updating lost item: {e}', 'danger')
    elif request.method == 'GET':
        form.title.data = item.title
        form.description.data = item.description
    return render_template('update_lost_item.html', form=form, item=item)

@app.route('/items/lost/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_lost_item(item_id):
    form = DeleteForm()
    if form.validate_on_submit():
        item = crud.get_lost_item(g.db, item_id)
        if not item:
            flash('Lost item not found.', 'danger')
            return redirect(url_for('items_lost_list'))
        try:
            crud.delete_lost_item(g.db, item_id)
            flash(f'Lost item "{item.title}" deleted successfully!', 'success')
        except Exception as e:
            flash(f'Error deleting lost item: {e}', 'danger')
    else:
        flash('Invalid request.', 'danger')
    return redirect(url_for('items_lost_list'))

if __name__ == '__main__':
    app.run(debug=True)