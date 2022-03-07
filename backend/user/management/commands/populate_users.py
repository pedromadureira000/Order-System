from django.core.management import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
from faker import Faker
from core.models import Company, User
import time


class Command(BaseCommand):
    def handle(self, *args, **options):
        faker = Faker()
        comp = Company.objects.get(company_code='123')

        for _ in range(30):
            username = faker.first_name()
            user = User.objects.create(
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                email=faker.email(),
                cpf="935.373.270-05",
                username=username,
                company=comp,
                user_code=username + "#" + comp.company_code,
            )
            user.set_password('asdf1234')
            user.save()

