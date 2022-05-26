# Generated by Django 4.0.4 on 2022-05-26 16:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organization', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('order', '0001_initial'),
        ('item', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderhistory',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AddField(
            model_name='ordereditem',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='item.item', verbose_name='item'),
        ),
        migrations.AddField(
            model_name='ordereditem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordered_items', to='order.order', verbose_name='order'),
        ),
        migrations.AddField(
            model_name='order',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='organization.client', verbose_name='client'),
        ),
        migrations.AddField(
            model_name='order',
            name='client_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='client user'),
        ),
        migrations.AddField(
            model_name='order',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='organization.company', verbose_name='company'),
        ),
        migrations.AddField(
            model_name='order',
            name='establishment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='organization.establishment', verbose_name='establishment'),
        ),
        migrations.AddField(
            model_name='order',
            name='items',
            field=models.ManyToManyField(through='order.OrderedItem', to='item.item', verbose_name='items'),
        ),
        migrations.AddField(
            model_name='order',
            name='price_table',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='item.pricetable', verbose_name='price table'),
        ),
        migrations.AddConstraint(
            model_name='ordereditem',
            constraint=models.UniqueConstraint(fields=('order', 'item'), name='OrderedItem unique_together'),
        ),
        migrations.AddConstraint(
            model_name='order',
            constraint=models.UniqueConstraint(fields=('client', 'order_number'), name='order compound primary key'),
        ),
    ]
