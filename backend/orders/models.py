from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.utils import timezone
from .utils import image_resize
from core.models import status_choices

class ItemTable(models.Model):
    #  Company_set
    # ItemCategory_set
    # Item_set
    class Meta:
        #  unique_together = (('contracting', 'item_table_code'),)
        constraints = [UniqueConstraint(fields=['contracting', 'item_table_code'], name='ItemTable compound primary key')]
    #  item_table_compound_id = models.CharField('Id da tabela de itens', max_length=10, primary_key=True, editable=False)
    contracting = models.ForeignKey('core.Contracting', on_delete=models.PROTECT, verbose_name="Contracting Company")
    item_table_code = models.SlugField("Item Table code", max_length=3)
    description = models.CharField(max_length=60, verbose_name="Description")
    note = models.TextField(blank=True, verbose_name="Note")


class Item(models.Model):
    # OrderedItem_set
    # PriceItem_set
    class Meta:
        verbose_name_plural = 'Itens'
        #  unique_together = (('item_table', 'item_code'),)
        constraints = [UniqueConstraint(fields=['item_table', 'item_code'], name='Item compound primary key')]
    item_table = models.ForeignKey('ItemTable', on_delete=models.PROTECT, verbose_name="Items Table")
    item_code = models.SlugField(max_length=15)
    category = models.ForeignKey('ItemCategory', on_delete=models.CASCADE, verbose_name="Category")
    description = models.CharField(max_length=60, verbose_name="Description")
    unit = models.CharField(max_length=10, verbose_name="Unit")
    barcode = models.CharField(max_length=13, verbose_name="Barcode")
    status = models.IntegerField(choices=status_choices)
    image = models.ImageField(default="images/items/defaultimage.jpeg", upload_to='images/items/')
    technical_description = models.TextField(blank=True)
    def __str__(self):
        return f'{self.item_code}'
    def save(self, *args, **kwargs):
        if self.image:
            image_resize(self.image, 115, 76.24)
        super().save(*args, **kwargs)


class ItemCategory(models.Model):
    #Item_set
    class Meta:
        #  unique_together = (('item_table', 'category_code'),)
        constraints = [UniqueConstraint(fields=['item_table', 'category_code'], name='ItemCategory compound primary key')]
    item_table = models.ForeignKey('ItemTable', on_delete=models.PROTECT, verbose_name="Items Table")
    category_code = models.SlugField(max_length=8)
    description = models.CharField(max_length=60)
    note = models.TextField(blank=True)
    def __str__(self):
        return f'Categoria: {self.description}'


class PriceTable(models.Model):
    #Order_set
    #PriceItem_set
    # ClientEstablishment_set
    class Meta:
        #  unique_together = (('company', 'table_code'),)
        constraints = [UniqueConstraint(fields=['company', 'table_code'], name='PriceTable compound primary key')]
    price_table_compound_id = models.SlugField(max_length=15) # 999#999#9999999
    company = models.ForeignKey('core.Company', on_delete=models.PROTECT)
    table_code = models.SlugField(max_length=7)
    description = models.CharField(max_length=60)
    items = models.ManyToManyField(Item, through='PriceItem')
    note = models.TextField(blank=True)
    def __str__(self):
        return f'{self.table_code}'


class PriceItem(models.Model):
    class Meta:
        #  unique_together = (('pricetable', 'item'),)
        constraints = [UniqueConstraint(fields=['pricetable', 'item'], name='PriceItem compound primary key')]
    pricetable = models.ForeignKey('PriceTable', on_delete=models.CASCADE, related_name='price_items', verbose_name="Price table")
    item = models.ForeignKey('Item', on_delete=models.PROTECT)
    price_unit = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="Unit Price")
    date = models.DateTimeField(auto_now_add=True)


class Order(models.Model):
    status_choices = (
        ("0", "Digitação"),
        ("1", "Transferido"),
        ("2", "Registrado"),
        ("3", "Faturado"),
        ("5", "Entregue"),
        ("9", "Cancelado")
    )
    # OrderedItem_set
    # OrderHistory_set
    class Meta:
        constraints = [UniqueConstraint(fields=['order_number', 'establishment'], name='order compound primary key')]
    order_number = models.IntegerField('Numero do pedido')
    client_user = models.ForeignKey('core.User', on_delete=models.PROTECT, verbose_name="Client User")
    company = models.ForeignKey('core.Company', on_delete=models.PROTECT)
    establishment = models.ForeignKey('core.Establishment', on_delete=models.PROTECT)
    pricetable = models.ForeignKey('PriceTable', on_delete=models.PROTECT)
    status = models.CharField(max_length=1, choices=status_choices)
    invoice_number = models.CharField(max_length=9, null=True)
    order_date = models.DateTimeField(default=timezone.now)
    billing_date = models.DateTimeField(blank=True, null=True, verbose_name="Billing Date")
    order_amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="Order amount")
    note = models.TextField(blank=True)
    def __str__(self):
        return f'Pedido N. {self.pk}'


class OrderedItem(models.Model):
    class Meta:
        constraints = [UniqueConstraint(fields=['order', 'item'], name='OrderedItem unique_together')]
        verbose_name = 'Ordered Item'
        verbose_name_plural = 'Ordered Items'
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    item = models.ForeignKey('Item', on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=11, decimal_places=2)
    unit_price = models.DecimalField(max_digits=11, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)


class OrderHistory(models.Model):
    type_choices = (
        (0, "Inclusão"),
        (1, "Alteração"),
        (2, "Exclusão"),
        (3, "Impressão"),
        (4, "Observação"),
    )
    user = models.ForeignKey('core.User', on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    history_type = models.IntegerField(choices=type_choices)
    history_description = models.TextField(blank=True)
