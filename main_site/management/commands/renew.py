from django.core.management.base import BaseCommand, CommandError
from user_info.models import User
from CCP.settings import BASE_DIR
import os
from django.core.management import call_command

class Command(BaseCommand):
    def handle(self, *args, **options):
        file_to_delete = []
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if "1_" in file:
                    file_to_delete.append(os.path.join(root, file))
        for file in file_to_delete:
            os.remove(file)
        os.remove(os.path.join(BASE_DIR,'db.sqlite3'))
        call_command('makemigrations')
        call_command('migrate')
        call_command('install')