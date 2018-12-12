"""
包括User和CcpMember两个表
User表用来存储用户的登录信息
CcpMember存储的是实际的入党信息
其他APP中的表把CcpMember作为外键

"""

from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.contrib.auth.models import User


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', False)
        return self._create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
    )
    USERNAME_FIELD = 'username'
    password = models.CharField(max_length=128)
    # 姓名
    real_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    is_admin = models.BooleanField(
        default=False,
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    student_id = models.TextField()
    photo_path = models.TextField()
    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        swappable = 'AUTH_USER_MODEL'

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)


class CcpMember(models.Model):
    student_id = models.TextField(default="Default")
    real_name = models.TextField(default="Default")
    branch = models.TextField(default="Default")
    current_state = models.TextField(default="Default")
    phone_number = models.TextField(default="Default")
    # 入党时间
    date = models.DateField()
    # 介绍人
    sponsor = models.TextField(default="Default")


class Branch(models.Model):
    # 支部名称
    branch_name = models.TextField(default="Default")
    # 支部书记
    branch_secretary_0 = models.TextField(default="Default")
    # 组织委员
    branch_secretary_1 = models.TextField(default="Default")
    # 宣传委员
    branch_secretary_2 = models.TextField(default="Default")
