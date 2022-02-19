from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from settings import settings
from django.contrib.auth import user_logged_in, user_logged_out
from .models import LoggedInUser

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)  # every time a user was created, a token will be generated fo that user.

# Signals fires when a user logs in and logs out. And send 'user' as positional argument

@receiver(user_logged_in)
def on_user_logged_in(sender, request, **kwargs):
    #  print('on_user_logged_in: ', datetime.now())
    obj, created = LoggedInUser.objects.get_or_create(user=kwargs.get('user'))   #get_or_create returns a tuple( created is a boolean )
    obj.session_key = request.session.session_key
    obj.save()

@receiver(user_logged_out)
def on_user_logged_out(sender, **kwargs):
    print('on_user_logged_out')
    LoggedInUser.objects.filter(user=kwargs.get('user')).delete()
    # I use filter function because in the OneSessionPerUserMiddleware i'm log out the request when an authenticated user does not have 
    # 'logged_in_user' (which will happen when user with more than one session logs out) 
    #  LoggedInUser.objects.get(user=kwargs.get('user')).delete()  <-- It could raise "LoggedInUser matching query does not exist"
