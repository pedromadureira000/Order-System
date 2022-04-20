from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import gettext_lazy as _
from item.models import Item

class Order(models.Model):
    status_choices = (
        (1, _('Typing')),
        (2, _('Transferred')),
        (3, _('Registered')),
        (4, _('Invoiced')),
        (5, _('Delivered')),
        (0, _('Canceled'))
    )
    # OrderedItem_set
    # OrderHistory_set
    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        constraints = [UniqueConstraint(fields=['client','establishment', 'order_number',], name='order compound primary key')]
    order_number = models.IntegerField(_('order number'), editable=False)
    client_user = models.ForeignKey('user.User', on_delete=models.PROTECT, verbose_name=_('client user'),)
    client = models.ForeignKey('organization.Client', on_delete=models.PROTECT, verbose_name=_('client'))
    company = models.ForeignKey('organization.Company', on_delete=models.PROTECT, verbose_name=_('company'))
    establishment = models.ForeignKey('organization.Establishment', on_delete=models.PROTECT, verbose_name=_('establishment'))
    price_table = models.ForeignKey('item.PriceTable', on_delete=models.PROTECT, verbose_name=_('price table'))
    items = models.ManyToManyField(Item, through='OrderedItem', verbose_name=_('items'))
    status = models.IntegerField(choices=status_choices)
    order_date = models.DateTimeField(auto_now_add=True, verbose_name=_('order date'))
    invoicing_date = models.DateTimeField(blank=True, null=True, verbose_name=_('invoicing date'))
    invoice_number = models.CharField(max_length=9, blank=True, verbose_name=_('invoice number'))
    order_amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name=_('order amount'))
    note = models.CharField(blank=True, verbose_name=_('note'), max_length=800)
    agent_note = models.CharField(blank=True, verbose_name=_('agent note'), max_length=800)
    def __str__(self):
        return f'Order N. {self.order_number}'

    def get_status_verbose_name(self, status):
        return [value[1] for value in Order._meta.get_field("status").choices if value[0] == status][0]

class OrderedItem(models.Model):
    class Meta:
        verbose_name = _('ordered Item')
        verbose_name_plural = _('ordered Items')
        constraints = [UniqueConstraint(fields=['order', 'item'], name='OrderedItem unique_together')]
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='ordered_items', verbose_name=_('order'))
    item = models.ForeignKey('item.Item', on_delete=models.PROTECT, verbose_name=_('item'))
    quantity = models.DecimalField(max_digits=11, decimal_places=2, verbose_name=_('quantity'))
    unit_price = models.DecimalField(max_digits=11, decimal_places=2, verbose_name=_('unit price'))
    date = models.DateTimeField(auto_now_add=True, verbose_name=_('date'))

class OrderHistory(models.Model):
    class Meta:
        verbose_name = _('order history')
        verbose_name_plural = _('order history')

    type_choices = (
        ('I', _('Inclusion')),
        ('A', _('Alteration')),
        ('N', _('Note')),
    )
    order = models.ForeignKey('Order', on_delete=models.DO_NOTHING, verbose_name=_('order'), related_name='order_history')
    user = models.ForeignKey('user.User', on_delete=models.DO_NOTHING, verbose_name=_('user'))
    history_type = models.CharField(choices=type_choices, max_length=2,verbose_name=_('history type'))
    history_description = models.CharField(verbose_name=_('history description'),max_length=800)
    agent_note = models.CharField(blank=True, verbose_name=_('agent note'), max_length=800)
    date = models.DateTimeField(auto_now_add=True, verbose_name=_('date'))
