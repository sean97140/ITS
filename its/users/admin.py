from django.contrib import admin
from .models import User


# Since we are using CAS we don't want users to
# worry about setting any kind of password.
class UserAdmin(admin.ModelAdmin):
    exclude = ('password',)

admin.site.register(User, UserAdmin)