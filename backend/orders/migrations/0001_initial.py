# Generated by Django 4.0.2 on 2022-02-15 18:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_compound_id', models.CharField(editable=False, max_length=23, unique=True, verbose_name='Item compound id')),
                ('item_code', models.SlugField(max_length=15)),
                ('description', models.CharField(max_length=60, verbose_name='Description')),
                ('unit', models.CharField(max_length=10, verbose_name='Unit')),
                ('barcode', models.CharField(blank=True, max_length=13, verbose_name='Barcode')),
                ('status', models.IntegerField(choices=[(1, 'Ativado'), (0, 'Desativado')])),
                ('image', models.ImageField(default='images/items/defaultimage.jpeg', upload_to='images/items/')),
                ('technical_description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'Itens',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.IntegerField(verbose_name='Numero do pedido')),
                ('status', models.CharField(choices=[('0', 'Digitação'), ('1', 'Transferido'), ('2', 'Registrado'), ('3', 'Faturado'), ('5', 'Entregue'), ('9', 'Cancelado')], max_length=1)),
                ('order_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('billing_date', models.DateTimeField(blank=True, null=True, verbose_name='Billing Date')),
                ('invoice_number', models.CharField(blank=True, max_length=9)),
                ('order_amount', models.DecimalField(decimal_places=2, max_digits=11, verbose_name='Order amount')),
                ('note', models.TextField(blank=True)),
                ('client_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Client User')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.company')),
                ('establishment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.establishment')),
            ],
        ),
        migrations.CreateModel(
            name='PriceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=11, verbose_name='Unit Price')),
                ('last_modified', models.DateTimeField(auto_now_add=True)),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='orders.item')),
            ],
        ),
        migrations.CreateModel(
            name='PriceTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_table_compound_id', models.SlugField(max_length=15)),
                ('table_code', models.SlugField(max_length=7)),
                ('description', models.CharField(max_length=60)),
                ('note', models.TextField(blank=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.company')),
                ('items', models.ManyToManyField(through='orders.PriceItem', to='orders.Item')),
            ],
        ),
        migrations.AddField(
            model_name='priceitem',
            name='price_table',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_items', to='orders.pricetable', verbose_name='Price table'),
        ),
        migrations.CreateModel(
            name='OrderHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('history_type', models.IntegerField(choices=[(0, 'Inclusão'), (1, 'Alteração'), (2, 'Exclusão'), (3, 'Impressão'), (4, 'Observação')])),
                ('history_description', models.TextField(blank=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderedItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=11)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=11)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='orders.item')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.order')),
            ],
            options={
                'verbose_name': 'Ordered Item',
                'verbose_name_plural': 'Ordered Items',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='price_table',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='orders.pricetable'),
        ),
        migrations.CreateModel(
            name='ItemTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_table_compound_id', models.CharField(editable=False, max_length=7, unique=True, verbose_name='Id da tabela de itens')),
                ('item_table_code', models.SlugField(max_length=3, verbose_name='Item Table code')),
                ('description', models.CharField(max_length=60, verbose_name='Description')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('contracting', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.contracting', verbose_name='Contracting Company')),
            ],
        ),
        migrations.CreateModel(
            name='ItemCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_compound_id', models.CharField(editable=False, max_length=16, unique=True, verbose_name='Item category compound id')),
                ('category_code', models.SlugField(max_length=8)),
                ('description', models.CharField(max_length=60)),
                ('note', models.TextField(blank=True)),
                ('item_table', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='orders.itemtable', verbose_name='Item Table')),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.itemcategory', verbose_name='Category'),
        ),
        migrations.AddField(
            model_name='item',
            name='item_table',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='orders.itemtable', verbose_name='Items Table'),
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
