from django.dispatch import receiver
from django.contrib.auth import user_logged_in, user_logged_out
from axes.signals import user_locked_out
from rest_framework.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

# Signals fires when a user logs in and logs out. And send 'user' as positional argument
@receiver(user_logged_in)
def on_user_logged_in(sender, request, **kwargs):
    #  print('on_user_logged_in: ', datetime.now())
    user = kwargs.get('user')
    user.current_session_key = request.session.session_key
    user.save()

@receiver(user_logged_out)
def on_user_logged_out(sender, **kwargs):
    print('on_user_logged_out')
    user = kwargs.get('user')
    user.current_session_key = ""
    user.save()

@receiver(user_locked_out)
def raise_permission_denied(*args, **kwargs):
    raise PermissionDenied(_("Locked out due to too many login failures. Please try again in a minute."))
