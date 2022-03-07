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
