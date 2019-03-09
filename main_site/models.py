from django.db import models


# Create your models here.
class Setting(models.Model):
    setting_name = models.TextField(unique=True)
    setting_value = models.TextField()


# 学期设置
class Semester(models.Model):
    semester_name = models.TextField(unique=True)
    semester_start_time = models.DateField()
    semester_end_time = models.DateField()
