from django.core.management import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
from core.models import Client, ClientEstablishment, ClientTable, Company, Contracting, Establishment, User
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
        comp = Company(name="PHSW-comp", company_compound_id="123#123", company_code='123', contracting=contracting, status=1)
        comp.save()
        estab = Establishment(name="PHSW-estab", establishment_compound_id="123#123#123",
                establishment_code='123', company=comp, status=1)
        estab.save()
        # --/ Client Table
        client_table = ClientTable(client_table_compound_id="123#11",contracting=contracting, client_table_code="11",
                description="string", note="string")
        client_table.save()
        # --/ Assign client table to company
        comp.client_table = client_table
        comp.save()
        # --/ Create client
        client = Client(client_compound_id="123#11#123", client_code="123", name="Client", client_table=client_table, status=1 )
        client.save()
        # --/ Create ClientEstablishment
        ClientEstablishment(establishment=estab, client=client).save()
       

