from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    class Meta:
        db_table = 'roles'
    def __str__(self): return self.name

class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='users')
    class Meta:
        db_table = 'users'
    def __str__(self): return self.username

class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    class Meta:
        db_table = 'items'
    def __str__(self): return self.name

class LostItem(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    class Meta:
        db_table = 'lost_items'
    def __str__(self): return self.name