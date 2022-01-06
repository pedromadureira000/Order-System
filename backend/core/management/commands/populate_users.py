from django.core.management import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
from faker import Faker
from core.models import User
import time


class Command(BaseCommand):
    def handle(self, *args, **options):
        faker = Faker()

        for _ in range(30):
            user = User.objects.create(
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                email=faker.email(),
                cpf=self.validated_data.get('cpf', '' ),
                username=faker.username()   # validate? TODO
                #  company=#????
                #  user_code=faker.
                password='',
            )
            user.set_password('1234')
            user.save()

