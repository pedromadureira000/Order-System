from django.db import models
from django.db.models.constraints import UniqueConstraint
from .utils import image_resize
from settings.utils import status_choices
from django.utils.translation import gettext_lazy as _

class ItemTable(models.Model):
    # Company_set
    # ItemCategory_set
    # Item_set
    class Meta:
        verbose_name = _('item table')
        verbose_name_plural = _('item tables')
        constraints = [UniqueConstraint(fields=['contracting', 'item_table_code'], name='ItemTable compound primary key')]
    item_table_compound_id = models.CharField(_('item table compound id'), max_length=7, unique=True, editable=False)
    contracting = models.ForeignKey('organization.Contracting', on_delete=models.PROTECT, verbose_name=_('contracting'))
    item_table_code = models.SlugField(max_length=3, verbose_name=_('item table code'))
    description = models.CharField(max_length=60, verbose_name=_('description'))
    note = models.CharField(blank=True, verbose_name=_('note'), max_length=800)
    def __str__(self):
        return f'Item Table: {self.description}'

class ItemCategory(models.Model):
    #Item_set
    class Meta:
        verbose_name = _('item category')
        verbose_name_plural = _('item categories')
        constraints = [UniqueConstraint(fields=['item_table', 'category_code'], name='ItemCategory compound primary key')]
    item_table = models.ForeignKey('ItemTable', on_delete=models.PROTECT, verbose_name="item table")
    category_compound_id = models.CharField(_('item category compound id'), max_length=16, unique=True, editable=False)
    category_code = models.SlugField(max_length=8, verbose_name=_('category code'))
    description = models.CharField(max_length=60, verbose_name=_('description'))
    note = models.CharField(blank=True, verbose_name=_('note'), max_length=800)
    def __str__(self):
        return f'Category: {self.description}'

class Item(models.Model):
    # OrderedItem_set
    # PriceItem_set
    class Meta:
        verbose_name = _('item')
        verbose_name_plural = _('items')
        constraints = [UniqueConstraint(fields=['item_table', 'item_code'], name='Item compound primary key')]
    item_table = models.ForeignKey('ItemTable', on_delete=models.PROTECT, verbose_name=_("item table"))
    item_compound_id = models.CharField(_('item compound id'), max_length=23, unique=True, editable=False) # 999&999&9x15
    item_code = models.SlugField(max_length=15, verbose_name=_('item code'))
    category = models.ForeignKey('ItemCategory', on_delete=models.CASCADE, verbose_name=_('category'))
    description = models.CharField(max_length=60, verbose_name=_('description'))
    unit = models.CharField(max_length=10, verbose_name=_('unit'))
    barcode = models.CharField(max_length=13,blank=True, verbose_name=_('barcode'))
    status = models.IntegerField(choices=status_choices, default=1)
    image = models.ImageField(default="images/items/defaultimage.jpeg", upload_to='images/items/', verbose_name=_('image'))
    technical_description = models.CharField(blank=True, verbose_name=_('technical description'), max_length=800)
    def __str__(self):
        return f'{self.item_code}'
    def save(self, *args, **kwargs):
        if self.image:
            image_resize(self.image, 115, 76.24)
        super().save(*args, **kwargs)

class PriceTable(models.Model):
    #Order_set
    #PriceItem_set
    # ClientEstablishment_set
    class Meta:
        verbose_name = _('price table')
        verbose_name_plural = _('price tables')
        constraints = [UniqueConstraint(fields=['company', 'table_code'], name='PriceTable compound primary key')]
    price_table_compound_id = models.SlugField(max_length=15, verbose_name=_('price table compound id'), unique=True, 
            editable=False) # 999&999&9999999
    company = models.ForeignKey('organization.Company', on_delete=models.PROTECT, verbose_name=_('company'))
    table_code = models.SlugField(max_length=7, verbose_name=_('table_code'))
    description = models.CharField(max_length=60, verbose_name=_('description'))
    items = models.ManyToManyField(Item, through='PriceItem', verbose_name=_('items'))
    note = models.CharField(blank=True, verbose_name=_('note'), max_length=800)
    def __str__(self):
        return f'{self.table_code}'

class PriceItem(models.Model):
    class Meta:
        verbose_name = _('price item')
        verbose_name_plural = _('price items')
        constraints = [UniqueConstraint(fields=['price_table', 'item'], name='PriceItem compound primary key')]
    price_table = models.ForeignKey('PriceTable', on_delete=models.CASCADE, related_name='price_items', 
            verbose_name=_('price table'))
    item = models.ForeignKey('Item', on_delete=models.PROTECT, verbose_name=_('item'))
    unit_price = models.DecimalField(max_digits=11, decimal_places=2, verbose_name=_('unit price'), default=0)
    last_modified = models.DateTimeField(auto_now=True, verbose_name=_('last modified'))
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_('creation date'))