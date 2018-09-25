from django.contrib.auth.models import AbstractUser
from django.db import models

class GeekUser(AbstractUser):
    # 邀请码
    invation_code = models.CharField(max_length=8)
    # 父邀请码
    par_invation_code = models.CharField(max_length=8)
    # 子邀请码
    sub_invation_code = models.TextField()
    # 微信登录用户标识
    wxuin = models.CharField(max_length=32)
    # 微信昵称
    nick_name = models.CharField(max_length=32)

class GeekCode(models.Model):
    # 邀请码
    invation_code = models.CharField(max_length=8)
    # 邀请码状态: 默认可用
    is_available = models.BooleanField(default=True)
