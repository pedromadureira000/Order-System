# Generated by Django 4.0.1 on 2022-01-17 15:24

import core.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_cpf_cnpj.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, verbose_name='username')),
                ('user_code', models.CharField(max_length=150, unique=True, verbose_name='User code')),
                ('first_name', models.CharField(max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(max_length=254, verbose_name='email address')),
                ('cpf', django_cpf_cnpj.fields.CPFField(blank=True, max_length=14, verbose_name='CPF')),
                ('note', models.CharField(blank=True, max_length=150)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', core.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='LoggedInUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, max_length=32, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='logged_in_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, verbose_name='Nome')),
                ('cnpj', django_cpf_cnpj.fields.CNPJField(blank=True, max_length=18, verbose_name='CNPJ')),
                ('client_code', models.CharField(blank=True, max_length=9, verbose_name='Código do cliente')),
                ('vendor_code', models.CharField(blank=True, max_length=9, verbose_name='Código do vendedor')),
                ('company_code', models.CharField(max_length=9, unique=True, verbose_name='Código da empresa')),
                ('status', models.CharField(choices=[('A', 'Ativado'), ('D', 'Desativado'), ('B', 'Bloqueado')], max_length=1)),
                ('company_type', models.CharField(choices=[('D', 'Distribuidora'), ('L', 'Lojista'), ('C', 'Contratante'), ('O', 'Outros')], max_length=1)),
                ('note', models.CharField(blank=True, max_length=150)),
                ('contracting_company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.company', verbose_name='Empresa Contratante')),
            ],
        ),
    ]
