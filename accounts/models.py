from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Create your models here.


class CustomUser(AbstractUser): 
    """ 拡 張 ユーザーモデル""" 
    class Meta(AbstractUser.Meta): 
        db_table = 'custom_user'

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


