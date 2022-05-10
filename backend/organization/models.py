from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import gettext_lazy as _
from django_cpf_cnpj.fields import CNPJField
from settings.utils import status_choices

class Contracting(models.Model):
    # ItemTable_set
    # ClientTable_set
    # Company_set
    # User_set
    class Meta:
        verbose_name = _('contracting')
        verbose_name_plural = _('contractings')
    contracting_code = models.SlugField(_("contracting code"), max_length=3, primary_key=True)
    name = models.CharField(max_length=60, verbose_name=_("name"))
    status = models.IntegerField(choices=status_choices, default=1)
    active_users_limit = models.IntegerField(default=5, verbose_name=_("active users limit"))
    note = models.CharField(blank=True, verbose_name=_('note'), max_length=800)
    def __str__(self):
        return f'Contracting: {self.name}'

class Company(models.Model):
    # Establishment_set
    # PriceTable_set
    class Meta:
        verbose_name = _('company')
        verbose_name_plural = _('companies')
        constraints = [UniqueConstraint(fields=['contracting', 'company_code'], name='Company compound primary key')]
    company_compound_id = models.CharField(_('company compound id'), max_length=7, primary_key=True) 
    contracting = models.ForeignKey('Contracting', on_delete=models.PROTECT, verbose_name=_('contracting'))
    company_code = models.SlugField(_('company code'), max_length=3)
    item_table = models.ForeignKey('item.ItemTable', blank=True, null=True, on_delete=models.PROTECT, verbose_name=_('item table'))
    client_table = models.ForeignKey('ClientTable', blank=True, null=True,on_delete=models.PROTECT, verbose_name=_('client table'))
    name = models.CharField(max_length=60, verbose_name=_('name'))
    cnpj_root = models.CharField(max_length=10, verbose_name=_('CNPJ root'))
    status = models.IntegerField(choices=status_choices, default=1)
    note = models.CharField(blank=True, verbose_name=_('note'), max_length=800)
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
    establishment_compound_id = models.CharField(_('establishment compound id'), max_length=11, primary_key=True) 
    company = models.ForeignKey('Company', on_delete=models.PROTECT, verbose_name=_('company'))
    establishment_code = models.SlugField(max_length=3, verbose_name=_('establishment code'))
    name = models.CharField(max_length=60, verbose_name=_("name"))
    cnpj = CNPJField(masked=True, verbose_name="CNPJ")
    status = models.IntegerField(choices=status_choices, default=1)
    note = models.CharField(blank=True, verbose_name=_('note'), max_length=800)
    def __str__(self):
        return f'Establishment: {self.name}'

class ClientTable(models.Model):
    #  Company_set
    #  Client_set
    class Meta:
        verbose_name = _('client table')
        verbose_name_plural = _('client tables')
        constraints = [UniqueConstraint(fields=['contracting', 'client_table_code'], name='ClientTable compound primary key')]
    client_table_compound_id = models.CharField(_('client table compound id'), max_length=7, primary_key=True)
    contracting = models.ForeignKey('Contracting', on_delete=models.PROTECT, verbose_name=_('contracting'))
    client_table_code = models.SlugField(_('client table code'), max_length=3)
    description = models.CharField(max_length=60, verbose_name=_('description'))
    note = models.CharField(blank=True, verbose_name=_('note'), max_length=800)

class Client(models.Model):
    # User_set
    # ClientEstablishment_set
    class Meta:
        verbose_name = 'client'
        verbose_name_plural = 'clients'
        constraints = [UniqueConstraint(fields=['client_table', 'client_code'], name='Client compound primary key')]
    client_compound_id = models.CharField(_('client compound id'), max_length=16, primary_key=True) 
    client_table = models.ForeignKey('ClientTable',on_delete=models.PROTECT, verbose_name=_('client table'))
    client_code = models.SlugField(max_length=6, verbose_name=_('client code'))
    vendor_code = models.CharField(blank=True, max_length=9, verbose_name=_('vendor code'))
    name = models.CharField(max_length=60, verbose_name=_('name'))
    cnpj = CNPJField(masked=True, verbose_name="CNPJ")
    status = models.IntegerField(choices=status_choices, default=1)
    establishments = models.ManyToManyField(Establishment, through='ClientEstablishment', verbose_name=_('establishments'))
    note = models.CharField(blank=True, verbose_name=_('note'), max_length=800)
    def __str__(self):
        return f'Cliente: {self.name}'

class ClientEstablishment(models.Model):
    class Meta:
        verbose_name = _('client establishment')
        verbose_name_plural = _('client establishments')
        constraints = [UniqueConstraint(fields=['client', 'establishment'], name='ClientEstablishment compound primary key')]
    establishment = models.ForeignKey('Establishment',on_delete=models.CASCADE, verbose_name=_('establishment')) 
    client = models.ForeignKey('Client',on_delete=models.CASCADE, related_name='client_establishments', verbose_name=_('client'))
    price_table = models.ForeignKey('item.PriceTable', null=True, on_delete=models.SET_NULL, verbose_name=_('price table'))

