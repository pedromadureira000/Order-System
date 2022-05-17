from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

status_choices = (
    (0, _("Disabled")),
    (1, _( "Active"))
)


def non_negative_number(value):
    if value < 0:
        raise serializers.ValidationError(_('This field cannot be an negative number.'))

def positive_number(value):
    if value <= 0:
        raise serializers.ValidationError(_('This field must be an positive number.'))

def has_permission(user, permission):
    return user.has_perm('user.' + permission)

def has_role(user, role):
    fake_cache = getattr(user, 'roles', None)
    if fake_cache:
        for key, value in fake_cache.items():
            if role == key:
                return value
        has_the_role = user.groups.filter(name=role).exists()
        user.fake_cache.append({role:has_the_role})
        return has_the_role
    else:
        user.fake_cache = []
        has_the_role = user.groups.filter(name=role).exists()
        user.fake_cache.append({role: has_the_role})
        return has_the_role


