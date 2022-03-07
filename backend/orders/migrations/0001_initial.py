# Generated by Django 4.0.3 on 2022-03-07 16:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_compound_id', models.CharField(editable=False, max_length=23, unique=True, verbose_name='item compound id')),
                ('item_code', models.SlugField(max_length=15, verbose_name='item code')),
                ('description', models.CharField(max_length=60, verbose_name='description')),
                ('unit', models.CharField(max_length=10, verbose_name='unit')),
                ('barcode', models.CharField(blank=True, max_length=13, verbose_name='barcode')),
                ('status', models.IntegerField(choices=[(0, 'Disabled'), (1, 'Active')], default=1)),
                ('image', models.ImageField(default='images/items/defaultimage.jpeg', upload_to='images/items/', verbose_name='image')),
                ('technical_description', models.CharField(blank=True, max_length=800, verbose_name='technical description')),
            ],
            options={
                'verbose_name': 'item',
                'verbose_name_plural': 'items',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.IntegerField(editable=False, verbose_name='order number')),
                ('status', models.IntegerField(choices=[(1, 'Typing'), (2, 'Transferred'), (3, 'Registered'), (4, 'Invoiced'), (5, 'Delivered'), (0, 'Canceled')])),
                ('order_date', models.DateTimeField(auto_now_add=True, verbose_name='order date')),
                ('invoicing_date', models.DateTimeField(blank=True, null=True, verbose_name='invoicing date')),
                ('invoice_number', models.CharField(blank=True, max_length=9, verbose_name='invoice number')),
                ('order_amount', models.DecimalField(decimal_places=2, max_digits=11, verbose_name='order amount')),
                ('note', models.CharField(blank=True, max_length=800, verbose_name='note')),
                ('agent_note', models.CharField(blank=True, max_length=800, verbose_name='agent note')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.client', verbose_name='client')),
                ('client_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='client user')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.company', verbose_name='company')),
                ('establishment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.establishment', verbose_name='establishment')),
            ],
            options={
                'verbose_name': 'order',
                'verbose_name_plural': 'orders',
            },
        ),
        migrations.CreateModel(
            name='PriceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='unit price')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='creation date')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='orders.item', verbose_name='item')),
            ],
            options={
                'verbose_name': 'price item',
                'verbose_name_plural': 'price items',
            },
        ),
        migrations.CreateModel(
            name='PriceTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_table_compound_id', models.SlugField(editable=False, max_length=15, unique=True, verbose_name='price table compound id')),
                ('table_code', models.SlugField(max_length=7, verbose_name='table_code')),
                ('description', models.CharField(max_length=60, verbose_name='description')),
                ('note', models.CharField(blank=True, max_length=800, verbose_name='note')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.company', verbose_name='company')),
                ('items', models.ManyToManyField(through='orders.PriceItem', to='orders.item', verbose_name='items')),
            ],
            options={
                'verbose_name': 'price table',
                'verbose_name_plural': 'price tables',
            },
        ),
        migrations.AddField(
            model_name='priceitem',
            name='price_table',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_items', to='orders.pricetable', verbose_name='price table'),
        ),
        migrations.CreateModel(
            name='OrderHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('history_type', models.CharField(choices=[('I', 'Inclusion'), ('A', 'Alteration'), ('N', 'Note')], max_length=2, verbose_name='history type')),
                ('history_description', models.CharField(max_length=800, verbose_name='history description')),
                ('agent_note', models.CharField(blank=True, max_length=800, verbose_name='agent note')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='order_history', to='orders.order', verbose_name='order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'order history',
                'verbose_name_plural': 'order history',
            },
        ),
        migrations.CreateModel(
            name='OrderedItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=11, verbose_name='quantity')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=11, verbose_name='unit price')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='orders.item', verbose_name='item')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordered_items', to='orders.order', verbose_name='order')),
            ],
            options={
                'verbose_name': 'ordered Item',
                'verbose_name_plural': 'ordered Items',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='items',
            field=models.ManyToManyField(through='orders.OrderedItem', to='orders.item', verbose_name='items'),
        ),
        migrations.AddField(
            model_name='order',
            name='price_table',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='orders.pricetable', verbose_name='price table'),
        ),
        migrations.CreateModel(
            name='ItemTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_table_compound_id', models.CharField(editable=False, max_length=7, unique=True, verbose_name='item table compound id')),
                ('item_table_code', models.SlugField(max_length=3, verbose_name='item table code')),
                ('description', models.CharField(max_length=60, verbose_name='description')),
                ('note', models.CharField(blank=True, max_length=800, verbose_name='note')),
                ('contracting', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.contracting', verbose_name='contracting')),
            ],
            options={
                'verbose_name': 'item table',
                'verbose_name_plural': 'item tables',
            },
        ),
        migrations.CreateModel(
            name='ItemCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_compound_id', models.CharField(editable=False, max_length=16, unique=True, verbose_name='item category compound id')),
                ('category_code', models.SlugField(max_length=8, verbose_name='category code')),
                ('description', models.CharField(max_length=60, verbose_name='description')),
                ('note', models.CharField(blank=True, max_length=800, verbose_name='note')),
                ('item_table', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='orders.itemtable', verbose_name='item table')),
            ],
            options={
                'verbose_name': 'item category',
                'verbose_name_plural': 'item categories',
            },
        ),
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.itemcategory', verbose_name='category'),
        ),
        migrations.AddField(
            model_name='item',
            name='item_table',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='orders.itemtable', verbose_name='item table'),
        ),
        migrations.AddConstraint(
            model_name='pricetable',
            constraint=models.UniqueConstraint(fields=('company', 'table_code'), name='PriceTable compound primary key'),
        ),
        migrations.AddConstraint(
            model_name='priceitem',
            constraint=models.UniqueConstraint(fields=('price_table', 'item'), name='PriceItem compound primary key'),
        ),
        migrations.AddConstraint(
            model_name='ordereditem',
            constraint=models.UniqueConstraint(fields=('order', 'item'), name='OrderedItem unique_together'),
        ),
        migrations.AddConstraint(
            model_name='order',
            constraint=models.UniqueConstraint(fields=('order_number', 'establishment'), name='order compound primary key'),
        ),
        migrations.AddConstraint(
            model_name='itemtable',
            constraint=models.UniqueConstraint(fields=('contracting', 'item_table_code'), name='ItemTable compound primary key'),
        ),
        migrations.AddConstraint(
            model_name='itemcategory',
            constraint=models.UniqueConstraint(fields=('item_table', 'category_code'), name='ItemCategory compound primary key'),
        ),
        migrations.AddConstraint(
            model_name='item',
            constraint=models.UniqueConstraint(fields=('item_table', 'item_code'), name='Item compound primary key'),
        ),
    ]
