import re
from rest_framework import serializers
from rolepermissions.checkers import has_permission, has_role

# ---------------/ DRF Serializer Field Validators

def OnlyLettersNumbersDashAndUnderscoreUsernameValidator(value):
    if not re.fullmatch('^[a-zA-Z0-9_.-]*$', value):
        raise serializers.ValidationError('The username must have only letters, numbers, "-" and "_".')


# ---------------/ Django Role Permissions Object Validators
def is_adminAgent_or_erpClient(user):
    return has_role(user, ['erp', 'admin_agent'])

def has_any_permission_to_create_user(user):
    return True if is_adminAgent_or_erpClient(user) or has_permission(user, 'create_client_user') else False

def has_permission_to_create_user(user, role):
    create_user_permission = "create_" + role
    if not has_permission(user, create_user_permission):
        return False
    return True

#  def do_client_exists(client_code):

def contracting_can_create_user(contracting):
    return True
