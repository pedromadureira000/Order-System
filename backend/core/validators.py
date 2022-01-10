import re
from rest_framework import serializers


def OnlyLettersNumbersDashAndUnderscoreUsernameValidator(value):
    if not re.fullmatch('^[a-zA-Z0-9_.-]*$', value):
        raise serializers.ValidationError('The username must have only letters, numbers, "-" and "_".')
