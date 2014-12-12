from django.contrib import admin
from .models import Item, Status, Action, Location, Category

admin.site.register(Item)
admin.site.register(Status)
admin.site.register(Action)
admin.site.register(Location)
admin.site.register(Category)


# Register your models here.
