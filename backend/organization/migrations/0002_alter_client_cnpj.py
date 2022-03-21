# Generated by Django 4.0.3 on 2022-03-14 17:58

from django.db import migrations
import django_cpf_cnpj.fields


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='cnpj',
            field=django_cpf_cnpj.fields.CNPJField(max_length=18, verbose_name='CNPJ'),
        ),
    ]