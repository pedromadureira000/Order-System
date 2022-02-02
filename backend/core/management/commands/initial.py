from django.core.management import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
from core.models import Company, Contracting, Establishment, User
import time


class Command(BaseCommand):
    def handle(self, *args, **options):
        contracting = Contracting(name="PHSW", contracting_code='123', status=1, active_users_limit=9999)
        contracting.save()
        user = User.objects.create_superuser(
            username="admin",
            first_name="Admin",
            last_name="adm",
            email="admin@admin.phsw",
            cpf="935.373.270-05",
            contracting=contracting,
            status=1,
            password='asdf'
        )
        comp = Company(name="PHSW-comp", company_id="123#123", company_code='123', contracting=contracting, status=1)
        comp.save()
        estab = Establishment(name="PHSW-estab", establishment_id="123#123#123", establishment_code='123', company=comp, status=1)
        estab.save()
        #  user.set_password('asdf1234')
        #  user.save()

