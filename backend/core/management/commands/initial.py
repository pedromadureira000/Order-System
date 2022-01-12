from django.core.management import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
from core.models import Company, User
import time


class Command(BaseCommand):
    def handle(self, *args, **options):
        comp = Company(name="PHSW", company_code='123', cnpj="40.229.893/0001-66", status="A", company_type="O")
        comp.save()
        print(comp)
        user = User.objects.create_superuser(
            first_name="Admin",
            last_name="adm",
            email="admin@admin.phsw",
            cpf="935.373.270-05",
            username="admin",
            company=comp.id,
            user_code="admin#123",
            is_superuser=True,
            is_staff=True
        )
        user.set_password('asdf1234')
        user.save()

