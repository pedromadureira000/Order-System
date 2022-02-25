# Generated by Django 4.0.2 on 2022-02-25 20:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_order_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='agent_note',
            field=models.CharField(blank=True, max_length=800, verbose_name='agent note'),
        ),
        migrations.AddField(
            model_name='order',
            name='items',
            field=models.ManyToManyField(through='orders.OrderedItem', to='orders.Item', verbose_name='items'),
        ),
        migrations.AddField(
            model_name='orderhistory',
            name='agent_note',
            field=models.CharField(blank=True, max_length=800, verbose_name='agent note'),
        ),
        migrations.AlterField(
            model_name='item',
            name='technical_description',
            field=models.CharField(blank=True, max_length=800, verbose_name='technical description'),
        ),
        migrations.AlterField(
            model_name='itemcategory',
            name='note',
            field=models.CharField(blank=True, max_length=800, verbose_name='note'),
        ),
        migrations.AlterField(
            model_name='itemtable',
            name='note',
            field=models.CharField(blank=True, max_length=800, verbose_name='note'),
        ),
        migrations.AlterField(
            model_name='order',
            name='note',
            field=models.CharField(blank=True, max_length=800, verbose_name='note'),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='order date'),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_number',
            field=models.IntegerField(editable=False, verbose_name='order number'),
        ),
        migrations.AlterField(
            model_name='ordereditem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordered_items', to='orders.order', verbose_name='order'),
        ),
        migrations.AlterField(
            model_name='orderhistory',
            name='history_description',
            field=models.CharField(blank=True, max_length=800, verbose_name='history description'),
        ),
        migrations.AlterField(
            model_name='priceitem',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='creation date'),
        ),
        migrations.AlterField(
            model_name='pricetable',
            name='note',
            field=models.CharField(blank=True, max_length=800, verbose_name='note'),
        ),
    ]
