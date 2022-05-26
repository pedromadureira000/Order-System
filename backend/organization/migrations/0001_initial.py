# Generated by Django 4.0.4 on 2022-05-26 16:25

from django.db import migrations, models
import django.db.models.deletion
import django_cpf_cnpj.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('item', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('client_compound_id', models.CharField(max_length=16, primary_key=True, serialize=False, verbose_name='client compound id')),
                ('client_code', models.SlugField(max_length=6, verbose_name='client code')),
                ('vendor_code', models.CharField(blank=True, max_length=9, verbose_name='vendor code')),
                ('name', models.CharField(max_length=60, verbose_name='name')),
                ('cnpj', django_cpf_cnpj.fields.CNPJField(max_length=18, verbose_name='CNPJ')),
                ('status', models.IntegerField(choices=[(0, 'Disabled'), (1, 'Active')], default=1)),
                ('note', models.CharField(blank=True, max_length=800, verbose_name='note')),
            ],
            options={
                'verbose_name': 'client',
                'verbose_name_plural': 'clients',
                'default_permissions': [],
            },
        ),
        migrations.CreateModel(
            name='ClientTable',
            fields=[
                ('client_table_compound_id', models.CharField(max_length=7, primary_key=True, serialize=False, verbose_name='client table compound id')),
                ('client_table_code', models.SlugField(max_length=3, verbose_name='client table code')),
                ('description', models.CharField(max_length=60, verbose_name='description')),
                ('note', models.CharField(blank=True, max_length=800, verbose_name='note')),
            ],
            options={
                'verbose_name': 'client table',
                'verbose_name_plural': 'client tables',
                'default_permissions': [],
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('company_compound_id', models.CharField(max_length=7, primary_key=True, serialize=False, verbose_name='company compound id')),
                ('company_code', models.SlugField(max_length=3, verbose_name='company code')),
                ('name', models.CharField(max_length=60, verbose_name='name')),
                ('cnpj_root', models.CharField(max_length=10, verbose_name='CNPJ root')),
                ('status', models.IntegerField(choices=[(0, 'Disabled'), (1, 'Active')], default=1)),
                ('note', models.CharField(blank=True, max_length=800, verbose_name='note')),
                ('client_table', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='organization.clienttable', verbose_name='client table')),
            ],
            options={
                'verbose_name': 'company',
                'verbose_name_plural': 'companies',
                'default_permissions': [],
            },
        ),
        migrations.CreateModel(
            name='Contracting',
            fields=[
                ('contracting_code', models.SlugField(max_length=3, primary_key=True, serialize=False, verbose_name='contracting code')),
                ('name', models.CharField(max_length=60, verbose_name='name')),
                ('status', models.IntegerField(choices=[(0, 'Disabled'), (1, 'Active')], default=1)),
                ('active_users_limit', models.IntegerField(default=5, verbose_name='active users limit')),
                ('note', models.CharField(blank=True, max_length=800, verbose_name='note')),
            ],
            options={
                'verbose_name': 'contracting',
                'verbose_name_plural': 'contractings',
                'default_permissions': [],
            },
        ),
        migrations.CreateModel(
            name='Establishment',
            fields=[
                ('establishment_compound_id', models.CharField(max_length=11, primary_key=True, serialize=False, verbose_name='establishment compound id')),
                ('establishment_code', models.SlugField(max_length=3, verbose_name='establishment code')),
                ('name', models.CharField(max_length=60, verbose_name='name')),
                ('cnpj', django_cpf_cnpj.fields.CNPJField(max_length=18, verbose_name='CNPJ')),
                ('status', models.IntegerField(choices=[(0, 'Disabled'), (1, 'Active')], default=1)),
                ('note', models.CharField(blank=True, max_length=800, verbose_name='note')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='organization.company', verbose_name='company')),
            ],
            options={
                'verbose_name': 'establishment',
                'verbose_name_plural': 'establishments',
                'default_permissions': [],
            },
        ),
        migrations.AddField(
            model_name='company',
            name='contracting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='organization.contracting', verbose_name='contracting'),
        ),
        migrations.AddField(
            model_name='company',
            name='item_table',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='item.itemtable', verbose_name='item table'),
        ),
        migrations.AddField(
            model_name='clienttable',
            name='contracting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='organization.contracting', verbose_name='contracting'),
        ),
        migrations.CreateModel(
            name='ClientEstablishment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_establishments', to='organization.client', verbose_name='client')),
                ('establishment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organization.establishment', verbose_name='establishment')),
                ('price_table', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='item.pricetable', verbose_name='price table')),
            ],
            options={
                'verbose_name': 'client establishment',
                'verbose_name_plural': 'client establishments',
                'default_permissions': [],
            },
        ),
        migrations.AddField(
            model_name='client',
            name='client_table',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='organization.clienttable', verbose_name='client table'),
        ),
        migrations.AddField(
            model_name='client',
            name='establishments',
            field=models.ManyToManyField(through='organization.ClientEstablishment', to='organization.establishment', verbose_name='establishments'),
        ),
        migrations.AddConstraint(
            model_name='establishment',
            constraint=models.UniqueConstraint(fields=('company', 'establishment_code'), name='Establishment compound primary key'),
        ),
        migrations.AddConstraint(
            model_name='company',
            constraint=models.UniqueConstraint(fields=('contracting', 'company_code'), name='Company compound primary key'),
        ),
        migrations.AddConstraint(
            model_name='clienttable',
            constraint=models.UniqueConstraint(fields=('contracting', 'client_table_code'), name='ClientTable compound primary key'),
        ),
        migrations.AddConstraint(
            model_name='clientestablishment',
            constraint=models.UniqueConstraint(fields=('client', 'establishment'), name='ClientEstablishment compound primary key'),
        ),
        migrations.AddConstraint(
            model_name='client',
            constraint=models.UniqueConstraint(fields=('client_table', 'client_code'), name='Client compound primary key'),
        ),
    ]
