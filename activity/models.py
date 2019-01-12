from django.db import models
from user_info.models import CcpMember


# Create your models here.
class Activity(models.Model):
    activity_name = models.CharField('活动名称', max_length=200, unique=True)
    time_length = models.IntegerField('活动时长')
    publishTime = models.DateTimeField('发布时间', auto_now=True)
    close_time = models.DateTimeField('报名截止时间')
    activity_time = models.DateTimeField('活动开始时间')
    present_person = models.IntegerField('报名人数',default=0)
    max_person = models.IntegerField('最大人数')
    content = models.TextField(default="")
    publisher = models.CharField('发布人', max_length=100)
    person_in_charge = models.TextField(default="")


class ActivityRecord(models.Model):
    student_id = models.TextField()
    real_name = models.TextField()
    activity_name = models.TextField()
    joinTime = models.DateTimeField('报名时间', auto_now=True)
    activity_time = models.DateTimeField('活动时间')
    time_length = models.IntegerField('活动时长')
    proof = models.TextField(default="")
    is_ok = models.BooleanField(default=False)
    auditor = models.TextField()
