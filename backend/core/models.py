from django.apps import apps
from django.contrib import auth
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_cpf_cnpj.fields import CNPJField
from rolepermissions.roles import assign_role

status_choices = (
    (0, _("Disabled")),
    (1, _( "Active"))
)

class Contracting(models.Model):
    # ItemTable_set
    # ClientTable_set
    # Company_set
    # User_set
    class Meta:
        verbose_name = _('contracting')
        verbose_name_plural = _('contractings')
    contracting_code = models.SlugField(_("contracting code"), max_length=3, unique=True)
    name = models.CharField(max_length=60, verbose_name=_("name"))
    status = models.IntegerField(choices=status_choices, default=1)
    active_users_limit = models.IntegerField(default=5, verbose_name=_("active users limit"))
    note = models.TextField(blank=True, verbose_name=_('note'))
    def __str__(self):
        return f'Contracting: {self.name}'

class Company(models.Model):
    # Establishment_set
    # PriceTable_set
    class Meta:
        verbose_name = _('company')
        verbose_name_plural = _('companies')
        constraints = [UniqueConstraint(fields=['contracting', 'company_code'], name='Company compound primary key')]
    company_compound_id = models.CharField(_('company compound id'), max_length=7, unique=True, editable=False) 
    contracting = models.ForeignKey('Contracting', on_delete=models.PROTECT, verbose_name=_('contracting'))
    company_code = models.SlugField(_('company code'), max_length=3)
    item_table = models.ForeignKey('orders.ItemTable', blank=True, null=True, on_delete=models.PROTECT, verbose_name=_('item table'))
    client_table = models.ForeignKey('ClientTable', blank=True, null=True,on_delete=models.PROTECT, verbose_name=_('client table'))
    name = models.CharField(max_length=60, verbose_name=_('name'))
    cnpj = models.CharField(max_length=10, verbose_name=_('CNPJ root'))
    status = models.IntegerField(choices=status_choices, default=1)
    note = models.TextField(blank=True, verbose_name=_('note'))
    def __str__(self):
        return f'Company: {self.name}'

class Establishment(models.Model):
    # ClientEstablishment_set
    # AgentEstablishment_set
    # Order_set
    class Meta:
        verbose_name = _('establishment')
        verbose_name_plural = _('establishments')
        constraints = [UniqueConstraint(fields=['company', 'establishment_code'], name='Establishment compound primary key')]
    establishment_compound_id = models.CharField(_('establishment compound id'), max_length=11, editable=False, unique=True) 
    company = models.ForeignKey('Company', on_delete=models.PROTECT, verbose_name=_('company'))
    establishment_code = models.SlugField(max_length=3, verbose_name=_('establishment code'))
    name = models.CharField(max_length=60, verbose_name=_("name"))
    cnpj = CNPJField(masked=True, verbose_name="CNPJ")
    status = models.IntegerField(choices=status_choices, default=1)
    note = models.TextField(blank=True, verbose_name=_('note'))
    def __str__(self):
        return f'Establishment: {self.name}'

class ClientTable(models.Model):
    #  Company_set
    #  Client_set
    class Meta:
        verbose_name = _('client table')
        verbose_name_plural = _('client tables')
        constraints = [UniqueConstraint(fields=['contracting', 'client_table_code'], name='ClientTable compound primary key')]
    client_table_compound_id = models.CharField(_('client table compound id'), max_length=6, unique=True, editable=False)
    contracting = models.ForeignKey('Contracting', on_delete=models.PROTECT, verbose_name=_('contracting'))
    client_table_code = models.SlugField(_('client table code'), max_length=2)
    description = models.CharField(max_length=60, verbose_name=_('description'))
    note = models.TextField(blank=True, verbose_name=_('note'))

class Client(models.Model):
    # User_set
    # ClientEstablishment_set
    class Meta:
        verbose_name = 'client'
        verbose_name_plural = 'clients'
        constraints = [UniqueConstraint(fields=['client_table', 'client_code'], name='Client compound primary key')]
    client_compound_id = models.CharField(_('client compound id'), max_length=16, editable=False, unique=True,) 
    client_table = models.ForeignKey('ClientTable',on_delete=models.PROTECT, verbose_name=_('client table'))
    client_code = models.SlugField(max_length=9, verbose_name=_('client code'))
    vendor_code = models.CharField(blank=True, max_length=9, verbose_name=_('vendor code'))
    name = models.CharField(max_length=60, verbose_name=_('name'))
    cnpj = models.CharField(max_length=10, verbose_name='CNPJ')
    status = models.IntegerField(choices=status_choices, default=1)
    establishments = models.ManyToManyField(Establishment, through='ClientEstablishment', verbose_name=_('establishments'))
    note = models.TextField(blank=True, verbose_name=_('note'))
    def __str__(self):
        return f'Cliente: {self.name}'

class ClientEstablishment(models.Model):
    class Meta:
        verbose_name = _('client establishment')
        verbose_name_plural = _('client establishments')
        constraints = [UniqueConstraint(fields=['client', 'establishment'], name='ClientEstablishment compound primary key')]
    establishment = models.ForeignKey('Establishment',on_delete=models.CASCADE, verbose_name=_('establishment')) 
    client = models.ForeignKey('Client',on_delete=models.CASCADE, related_name='client_establishments', verbose_name=_('client'))
    price_table = models.ForeignKey('orders.PriceTable', blank=True, null=True, on_delete=models.SET_NULL, 
            verbose_name=_('price table'))

class AgentEstablishment(models.Model):
    class Meta:
        verbose_name = _('agent establishment')
        verbose_name_plural = _('agent establishments')
        constraints = [UniqueConstraint(fields=['agent', 'establishment'], name='AgentEstablishment compound primary key')]
    establishment = models.ForeignKey('Establishment',on_delete=models.PROTECT, verbose_name=_('establishment'))
    agent = models.ForeignKey('User',on_delete=models.CASCADE, related_name='agent_establishments', verbose_name=_('agent'))

class UserManager(BaseUserManager):
    use_in_migrations = True
    def _create_user(self, username, contracting, password, **extra_fields):
        """
        Create and save a user with the given username, contracting, and password.
        """
        if not username:
            raise ValueError('A username must be set')
        if not contracting:
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
        user_code = username + "#" + contracting.contracting_code
        user = self.model(user_code=user_code,username=username, contracting=contracting, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        if user.is_superuser:
            assign_role(user, 'erp')
        return user
    def create_user(self, username=None, contracting=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, contracting, password, **extra_fields)
    def create_superuser(self, username, contracting=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(username, contracting, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    # AgentEstablishment_set
    # OrderHistory_set
    # Order_set
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        constraints = [UniqueConstraint(fields=['username', 'contracting'], name='Username compound primary key')]
    contracting = models.ForeignKey('Contracting', on_delete=models.PROTECT, verbose_name=_('contracting'))
    client = models.ForeignKey('Client', on_delete=models.PROTECT, null=True, blank=True, verbose_name=_("client company"))
    establishments = models.ManyToManyField("Establishment", through='AgentEstablishment', verbose_name=_("agent establishments"))
    user_code = models.CharField(_('user code'), max_length=50, unique=True, editable=False)
    username = models.SlugField(_('username'), max_length=50)
    first_name = models.CharField(_('first name'), max_length=50, blank=True)
    last_name = models.CharField(_('last name'), max_length=50, blank=True)
    email = models.EmailField('email')
    status = models.IntegerField(choices=status_choices, default=1)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    note = models.TextField(blank=True, verbose_name=_('note'))
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
