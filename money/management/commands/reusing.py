from django.core.management.base import BaseCommand
from os import system, chdir
from sys import path
path.append("money/reusing")
from github import download_from_github


class Command(BaseCommand):
    help = 'Update reusing project'

    def handle(self, *args, **options):
        download_from_github("turulomio", "reusingcode", "python_plain/currency.py", "money/reusing")
        download_from_github("turulomio", "reusingcode", "python_plain/github.py", "money/reusing")

