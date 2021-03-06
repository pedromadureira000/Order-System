# Generated by Django 4.0.4 on 2022-05-26 16:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import user.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organization', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('user_code', models.CharField(max_length=50, primary_key=True, serialize=False, verbose_name='user code')),
                ('username', models.SlugField(verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=50, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=50, verbose_name='last name')),
                ('email', models.EmailField(max_length=254, verbose_name='email')),
                ('status', models.IntegerField(choices=[(0, 'Disabled'), (1, 'Active')], default=1)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('note', models.CharField(blank=True, max_length=800, verbose_name='note')),
                ('current_session_key', models.CharField(blank=True, max_length=32, null=True, verbose_name='sesssion key')),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='organization.client', verbose_name='client company')),
                ('contracting', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='organization.contracting', verbose_name='contracting')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'default_permissions': [],
            },
            managers=[
                ('objects', user.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AgentEstablishment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agent_establishments', to=settings.AUTH_USER_MODEL, verbose_name='agent')),
                ('establishment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='organization.establishment', verbose_name='establishment')),
            ],
            options={
                'verbose_name': 'agent establishment',
                'verbose_name_plural': 'agent establishments',
                'default_permissions': [],
            },
        ),
        migrations.AddField(
            model_name='user',
            name='establishments',
            field=models.ManyToManyField(through='user.AgentEstablishment', to='organization.establishment', verbose_name='agent establishments'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
        migrations.AddConstraint(
            model_name='agentestablishment',
            constraint=models.UniqueConstraint(fields=('agent', 'establishment'), name='AgentEstablishment compound primary key'),
        ),
        migrations.AddConstraint(
            model_name='user',
            constraint=models.UniqueConstraint(fields=('username', 'contracting'), name='Username compound primary key'),
        ),
    ]
