# perms.py
from permissions import PermissionsRegistry

# create a registry to tack permissions onto
permissions = PermissionsRegistry()

@permissions.register
def can_create_car(user):
    return user.is_staff
    
@permissions.register
def can_view_item(user):
    return user.is_staff