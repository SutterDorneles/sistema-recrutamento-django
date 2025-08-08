import sys
from django.core.management import call_command
import django

django.setup()

with open('backup_dados.json', 'w', encoding='utf-8') as f:
    call_command('dumpdata', '--exclude=auth.permission', '--exclude=contenttypes', indent=2, stdout=f)
