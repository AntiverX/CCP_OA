from django.db import models
from user_info.models import CcpMember


# Create your models here.
class Activity(models.Model):
    activityName = models.CharField('活动名称', max_length=200)
    publishTime = models.DateTimeField('发布时间', auto_now=True)
    closeTime = models.DateTimeField('报名截止时间')
    activityTime = models.DateTimeField('活动开始时间')
    timeLength = models.IntegerField('活动时长')
    activityState = models.CharField('活动状态', max_length=150)
    presentPerson = models.IntegerField('报名人数')
    maxPerson = models.IntegerField('最大人数')
    publisher = models.CharField('发布人', max_length=100)


class AttendanceRecord(models.Model):
    ccp_member = models.ForeignKey(CcpMember, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    joinTime = models.DateTimeField('报名时间', auto_now=True)
