from django.core.management.base import BaseCommand, CommandError
from user_info.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        admin = User.objects.create_user(
            username="Antiver",
            password="wang@85#2",
            email="antiver@foxmail.com",
            real_name="王帅鹏",
            student_id="3120180863",
            is_admin=1,
        )
        admin.save()