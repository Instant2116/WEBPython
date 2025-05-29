from django import forms
from .models import Role, User, Item, LostItem

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name']

class UserForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description']

class LostItemForm(forms.ModelForm):
    class Meta:
        model = LostItem
        fields = ['name', 'description']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'role']

class ItemUpdateForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description']

class LostItemUpdateForm(forms.ModelForm):
    class Meta:
        model = LostItem
        fields = ['name', 'description']