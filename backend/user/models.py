from django.apps import apps
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rolepermissions.roles import assign_role
from settings.utils import status_choices


class AgentEstablishment(models.Model):
    class Meta:
        verbose_name = _('agent establishment')
        verbose_name_plural = _('agent establishments')
        constraints = [UniqueConstraint(fields=['agent', 'establishment'], name='AgentEstablishment compound primary key')]
    establishment = models.ForeignKey('organization.Establishment',on_delete=models.PROTECT, verbose_name=_('establishment'))
    agent = models.ForeignKey('User',on_delete=models.CASCADE, related_name='agent_establishments', verbose_name=_('agent'))

class UserManager(BaseUserManager):
    use_in_migrations = True
    def _create_user(self, username, contracting_id, password, **extra_fields):
        """
        Create and save a user with the given username, contracting_id, and password.
        """
        if not username:
            raise ValueError('A username must be set')
        if not contracting_id:
            raise ValueError('A contracting must be set')
        if not password:
            raise ValueError('A password must be set')
        if not extra_fields.get('status'):
            raise ValueError('A status must be set')
        #  email = self.normalize_email(email)
        GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        username = GlobalUserModel.normalize_username(username)
        user_code = contracting_id + "*" + username
        user = self.model(user_code=user_code,username=username, contracting_id=contracting_id, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        if user.is_superuser:
            assign_role(user, 'super_user')
        return user
    def create_user(self, username=None, contracting_id=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, contracting_id, password, **extra_fields)
    def create_superuser(self, username, contracting_id=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(username, contracting_id, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    # AgentEstablishment_set
    # OrderHistory_set
    # Order_set
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        constraints = [UniqueConstraint(fields=['username', 'contracting'], name='Username compound primary key')]
    contracting = models.ForeignKey('organization.Contracting', on_delete=models.PROTECT, verbose_name=_('contracting'))
    client = models.ForeignKey('organization.Client', on_delete=models.PROTECT, null=True, blank=True, verbose_name=_("client company"))
    establishments = models.ManyToManyField("organization.Establishment", through='AgentEstablishment', verbose_name=_("agent establishments"))
    user_code = models.CharField(_('user code'), max_length=50, primary_key=True)
    username = models.SlugField(_('username'), max_length=50)
    first_name = models.CharField(_('first name'), max_length=50, blank=True)
    last_name = models.CharField(_('last name'), max_length=50, blank=True)
    email = models.EmailField('email')
    status = models.IntegerField(choices=status_choices, default=1)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    note = models.CharField(blank=True, verbose_name=_('note'), max_length=800)
    objects = UserManager()
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'user_code'
    REQUIRED_FIELDS = ['username', 'contracting']
    # REQUIRED_FIELDS must contain all required fields on your user model, but should not contain the USERNAME_FIELD or
    # password as these fields will always be prompted for.
    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)
    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

class LoggedInUser(models.Model):
    user = models.OneToOneField(User, related_name='logged_in_user', on_delete=models.CASCADE, verbose_name=_('user'))
    # Session keys are 32 characters long
    session_key = models.CharField(max_length=32, null=True, blank=True, verbose_name=_('sesssion key'))
    def __str__(self):
        return self.user.first_name
