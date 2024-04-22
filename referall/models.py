
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import random
import string

def generate_auth_code():
    return ''.join(random.choices(string.digits, k=4))

def generate_invite_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

class NewUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone number must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)

class NewUser(AbstractBaseUser):
    phone_number = models.CharField(max_length=15, unique=True)
    auth_code = models.CharField(max_length=4, blank=True)
    invite_code = models.CharField(max_length=6, unique=True, default=generate_invite_code)
    activated_invite_code = models.CharField(max_length=6, blank=True)
    invited_users = models.ManyToManyField('self', symmetrical=False, related_name='invited_by', blank=True)


    def invited_users_count(self):
        return NewUser.objects.filter(
            invited_by__invite_code=self.invite_code).count()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = NewUserManager()