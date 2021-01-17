from django.core.management.base import BaseCommand
from sys import path
path.append("money/reusing")
from github import download_from_github


class Command(BaseCommand):
    help = 'Update reusing project'

    def handle(self, *args, **options):
        download_from_github("turulomio", "reusingcode", "python/call_by_name.py", "money/reusing")
        download_from_github("turulomio", "reusingcode", "python/listdict_functions.py", "money/reusing")
        download_from_github("turulomio", "reusingcode", "django/tabulator.py", "money/reusing")
        download_from_github("turulomio", "reusingcode", "django/decorators.py", "money/reusing")
        download_from_github("turulomio", "reusingcode", "python/lineal_regression.py", "money/reusing")
        download_from_github("turulomio", "reusingcode", "python_plain/casts.py", "money/reusing")
        download_from_github("turulomio", "reusingcode", "python_plain/currency.py", "money/reusing")
        download_from_github("turulomio", "reusingcode", "python_plain/github.py", "money/reusing")
        download_from_github("turulomio", "reusingcode", "python/datetime_functions.py", "money/reusing")
        download_from_github("turulomio", "reusingcode", "python_plain/myconfigparser.py", "money/reusing")
        download_from_github("turulomio", "reusingcode", "python/text_inputs.py", "money/reusing")
        download_from_github("turulomio", "reusingcode", "django/templatetags/mymenu.py", "money/templatetags")
        download_from_github("turulomio", "reusingcode", "js/component.ajaxbutton.js", "money/static/js")
        download_from_github("turulomio", "reusingcode", "js/component.yearmonthpicker.js", "money/static/js")
        download_from_github("turulomio", "reusingcode", "js/component.yearpicker.js", "money/static/js")
 
