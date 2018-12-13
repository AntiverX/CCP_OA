from django.core.management.base import BaseCommand, CommandError
from user_info.models import User
from activity.models import Activity
from django.core.management import call_command

class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command("renew")
        admin = User.objects.create_user(
            username="Antiver",
            password="wang@85#2",
            email="antiver@foxmail.com",
            real_name="王帅鹏",
            student_id="3120180863",
            is_admin=1,
            is_teacher=1,
            is_gxh=1
        )
        admin.save()
        new_activity = Activity.objects.create(
            activity_name="红色1+1",
            time_length=1,
            max_person=1,
            activity_time="2018-11-11 11:11",
            close_time="2018-11-11 11:11",
            publisher="王帅鹏",
        )
        new_activity.save()
