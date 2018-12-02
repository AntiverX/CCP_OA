from django.db import models
from user_info.models import CcpMember


# Create your models here.
class CourseInfo(models.Model):
    # 存储了参加的党课信息
    student_id = models.TextField()
    real_name = models.TextField()
    name = models.TextField()
    date = models.DateField()
    score = models.TextField()
    auditor = models.TextField()


class DocumentInfo(models.Model):
    # 存储了提交的入党材料信息
    student_id = models.TextField()
    real_name = models.TextField()
    name = models.TextField()
    date = models.DateField()
    is_ok = models.TextField()
    auditor = models.TextField()
