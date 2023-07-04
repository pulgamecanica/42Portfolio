import os
import requests
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Sync the database with the intra api"

    def add_arguments(self, parser):
        parser.add_argument('cmd',
                            choices=['user', 'project', 'cursus', 'skill', 'relations'],
                            action='store',
                            help='What to update in the database from the api',
                            metavar='sub-command',
                            type=str)
        parser.add_argument('intra_ids',
                            nargs='*',
                            action='store',
                            help='Which intra id(s) to update',
                            metavar='intra id',
                            type=int)

    def handle(self, *args, **options):
        print(F"cmd: {options['cmd']}")
        print(F"id's: {options['intra_ids']}")

