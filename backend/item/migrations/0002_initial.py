# Generated by Django 4.0.3 on 2022-04-29 17:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('item', '0001_initial'),
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pricetable',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='organization.company', verbose_name='company'),
        ),
        migrations.AddField(
            model_name='pricetable',
            name='items',
            field=models.ManyToManyField(through='item.PriceItem', to='item.item', verbose_name='items'),
        ),
        migrations.AddField(
            model_name='priceitem',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='item.item', verbose_name='item'),
        ),
        migrations.AddField(
            model_name='priceitem',
            name='price_table',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_items', to='item.pricetable', verbose_name='price table'),
        ),
        migrations.AddField(
            model_name='itemtable',
            name='contracting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='organization.contracting', verbose_name='contracting'),
        ),
        migrations.AddField(
            model_name='itemcategory',
            name='item_table',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='item.itemtable', verbose_name='item table'),
        ),
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='item.itemcategory', verbose_name='category'),
        ),
        migrations.AddField(
            model_name='item',
            name='item_table',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='item.itemtable', verbose_name='item table'),
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
