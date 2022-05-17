from django.dispatch import receiver
from django.contrib.auth import user_logged_in, user_logged_out

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
