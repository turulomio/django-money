from django.apps import AppConfig
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from money.signals import create_user_profile, save_user_profile


class MoneyConfig(AppConfig):
    name = 'money'


    def ready(self):
        post_save.connect(after_user_creation, sender=User)

