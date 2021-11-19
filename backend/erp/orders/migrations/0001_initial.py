# Generated by Django 3.2.9 on 2021-11-16 17:58

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_code', models.CharField(max_length=15, unique=True)),
                ('verbose_name', models.CharField(max_length=50, verbose_name='Nome')),
                ('description', models.TextField(default='sem descrição', verbose_name='Descrição')),
                ('unit', models.CharField(max_length=10, verbose_name='Unidade')),
                ('bar_code', models.CharField(max_length=13, verbose_name='Código de barras')),
                ('active', models.BooleanField(verbose_name='Ativado')),
                ('image', models.ImageField(default='images/items/defaultimage.jpeg', upload_to='images/items/')),
            ],
            options={
                'verbose_name_plural': 'Itens',
            },
        ),
        migrations.CreateModel(
            name='ItemCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_code', models.CharField(max_length=8, unique=True)),
                ('description', models.TextField(default='sem descrição', verbose_name='Descrição')),
                ('verbose_name', models.CharField(max_length=15, verbose_name='Nome')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('0', 'Digitação'), ('1', 'Transferido'), ('2', 'Registrado'), ('3', 'Faturado'), ('5', 'Entregue'), ('9', 'Cancelado')], max_length=1)),
                ('order_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Data do pedido')),
                ('billing_date', models.DateTimeField(blank=True, null=True, verbose_name='Data do faturamento')),
                ('order_amount', models.DecimalField(decimal_places=2, max_digits=11, verbose_name='Valor total')),
            ],
        ),
        migrations.CreateModel(
            name='PriceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_unit', models.DecimalField(decimal_places=2, max_digits=11, verbose_name='Preço unitario')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Data')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.item', verbose_name='Item')),
            ],
        ),
        migrations.CreateModel(
            name='PriceTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_code', models.CharField(max_length=7, unique=True)),
                ('verbose_name', models.CharField(max_length=50, verbose_name='Nome')),
                ('items', models.ManyToManyField(through='orders.PriceItem', to='orders.Item')),
            ],
        ),
        migrations.AddField(
            model_name='priceitem',
            name='pricetable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_items', to='orders.pricetable', verbose_name='Tabela de preço'),
        ),
        migrations.CreateModel(
            name='OrderedItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=11, verbose_name='Quantidade')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=11, verbose_name='Preço unitario')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Data')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='orders.item', verbose_name='Item')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.order', verbose_name='Pedido')),
            ],
            options={
                'verbose_name': 'Item do pedido',
                'verbose_name_plural': 'Itens do pedido',
            },
        ),
    ]
