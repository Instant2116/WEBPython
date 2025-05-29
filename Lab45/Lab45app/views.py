from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .forms import UserForm, RoleForm, ItemForm, LostItemForm, \
    UserUpdateForm, ItemUpdateForm, LostItemUpdateForm
from .models import User, Role, Item, LostItem


def get_logged_in_user(request):
    """
    Retrieves the User object from the database based on the user_id stored in the session.
    This simulates a logged-in user for the lab's simplified authentication.
    """
    user_id = request.session.get('user_id')
    if user_id:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:

            del request.session['user_id']
            return None
    return None


def admin_required(view_func):
    """
    Decorator to restrict access to views only to users with the 'Admin' role.
    Redirects to login if not logged in, or shows 403 if not an Admin.
    """

    def _wrapped_view_func(request, *args, **kwargs):
        user = get_logged_in_user(request)
        if not user:
            return redirect(reverse('login'))

        if user.role.name != 'Admin':
            return HttpResponse("Access Denied: You do not have permission to view this page.", status=403)

        return view_func(request, *args, **kwargs)

    return _wrapped_view_func


@require_http_methods(["GET", "POST"])
def login_page(request):
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username, password=password)
            request.session['user_id'] = user.id
            return redirect(reverse('dashboard'))
        except User.DoesNotExist:
            error_message = "Invalid username or password."

    return render(request, 'login.html', {'error_message': error_message})


@require_http_methods(["GET", "POST"])
def register_page(request):
    form = UserForm()
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = request.POST.get('password')
            user.save()
            return redirect(reverse('login'))
    return render(request, 'register.html', {'form': form})


@require_http_methods(["GET"])
def logout_page(request):
    """Logs out the user by clearing their session ID."""
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect(reverse('login'))


@require_http_methods(["GET"])
def dashboard_page(request):
    user_obj = get_logged_in_user(request)
    if not user_obj:
        return redirect(reverse('login'))
    return render(request, 'dashboard.html', {'user_obj': user_obj})


@require_http_methods(["GET"])
@admin_required
def users_list(request):
    users = User.objects.all()

    return render(request, 'users_list.html', {'users': users})


@require_http_methods(["GET"])
@admin_required
def user_detail(request, user_id):
    user_to_view = get_object_or_404(User, id=user_id)
    return render(request, 'user_detail.html', {'user_obj': user_to_view})


@require_http_methods(["GET", "POST"])
@admin_required
def user_edit(request, user_id):
    user_to_edit = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            form.save()
            return redirect(reverse('users_list'))
    else:
        form = UserUpdateForm(instance=user_to_edit)
    return render(request, 'user_edit.html', {'form': form, 'user_obj': user_to_edit})


@require_http_methods(["POST"])
@csrf_exempt
@admin_required
def user_delete(request, user_id):
    user_to_delete = get_object_or_404(User, id=user_id)
    user_to_delete.delete()
    return redirect(reverse('users_list'))


@require_http_methods(["GET"])
@admin_required
def roles_list(request):
    roles = Role.objects.all()
    return render(request, 'roles_list.html', {'roles': roles})


@require_http_methods(["GET", "POST"])
@admin_required
def role_create(request):
    form = RoleForm()
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('roles_list'))
    return render(request, 'role_create.html', {'form': form})


@require_http_methods(["GET", "POST"])
@admin_required
def role_edit(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            return redirect(reverse('roles_list'))
    else:
        form = RoleForm(instance=role)
    return render(request, 'role_edit.html', {'form': form, 'role': role})


@require_http_methods(["POST"])
@csrf_exempt
@admin_required
def role_delete(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    role.delete()
    return redirect(reverse('roles_list'))


@require_http_methods(["GET"])
def items_found_list(request):
    user_obj = get_logged_in_user(request)
    if not user_obj:
        return redirect(reverse('login'))
    items = Item.objects.all()
    return render(request, 'items_found_list.html', {'items': items, 'user_obj': user_obj})


@require_http_methods(["GET", "POST"])
@admin_required
def item_found_create(request):
    form = ItemForm()
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('items_found_list'))
    return render(request, 'item_found_create.html', {'form': form})


@require_http_methods(["GET", "POST"])
@admin_required
def item_found_edit(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST':
        form = ItemUpdateForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect(reverse('items_found_list'))
    else:
        form = ItemUpdateForm(instance=item)
    return render(request, 'item_found_edit.html', {'form': form, 'item': item})


@require_http_methods(["POST"])
@csrf_exempt
@admin_required
def item_found_delete(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    item.delete()
    return redirect(reverse('items_found_list'))


@require_http_methods(["GET"])
def items_lost_list(request):
    user_obj = get_logged_in_user(request)
    if not user_obj:
        return redirect(reverse('login'))
    items = LostItem.objects.all()
    return render(request, 'items_lost_list.html', {'items': items, 'user_obj': user_obj})


@require_http_methods(["GET", "POST"])
@admin_required
def lost_item_create(request):
    form = LostItemForm()
    if request.method == 'POST':
        form = LostItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('items_lost_list'))
    return render(request, 'lost_item_create.html', {'form': form})


@require_http_methods(["GET", "POST"])
@admin_required
def lost_item_edit(request, item_id):
    item = get_object_or_404(LostItem, id=item_id)
    if request.method == 'POST':
        form = LostItemUpdateForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect(reverse('items_lost_list'))
    else:
        form = LostItemUpdateForm(instance=item)
    return render(request, 'lost_item_edit.html', {'form': form, 'item': item})


@require_http_methods(["POST"])
@csrf_exempt
@admin_required
def lost_item_delete(request, item_id):
    item = get_object_or_404(LostItem, id=item_id)
    item.delete()
    return redirect(reverse('items_lost_list'))
