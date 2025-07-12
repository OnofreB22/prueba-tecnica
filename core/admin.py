from django.contrib import admin
from .models import User, UserAction

admin.site.register(User)
admin.site.register(UserAction)
