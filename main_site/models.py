from django.db import models


# Create your models here.
class Setting(models.Model):
    setting_name = models.TextField(unique=True)
    setting_value = models.TextField()