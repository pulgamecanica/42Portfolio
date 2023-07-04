import os
import requests
from pathlib import Path
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Sync the database with the intra api"

    def add_arguments(self, parser):
        parser.add_argument('cmd',
                            # 'user', 'project', 'cursus' and 'skill' each update their respective tables
                            # 'all' will update the models above and the relations between them
                            # 'relations' will update the relations between the models
                            # 'clear_cache' will clear the cache folder
                            choices=['user', 'project', 'cursus', 'skill', 'all',
                                     'relations', 'clear_cache'],
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
        parser.add_argument('--no-cache',
                            action='store_true',
                            dest="no_cache",
                            help='If it should not cache responses from the api',
                            default=False)
        parser.add_argument('--cache-dir',
                            action='store',
                            dest='cache_dir',
                            help='Where to store and read the cache',
                            default=Path("./cache"),
                            type=Path)
        parser.add_argument('--no-logfile',
                            action='store_true',
                            dest="no_logs",
                            help='If it should not create a logfile',
                            default=False)
        parser.add_argument('--log-dir',
                            action='store',
                            dest='log_dir',
                            help='Where to store the logs',
                            default=Path("./logs"),
                            type=Path)



    def handle(self, *args, **options):
        print('running with the following arguments:')
        print(f"verbosity: {options['verbosity']}")
        print(F"cmd: {options['cmd']}")
        print(F"id's: {options['intra_ids']}")
        print(F"cache: {'No cache' if options['no_cache'] else options['cache_dir'].resolve()}")
        print(F"logs: {'No logs' if options['no_logs'] else options['log_dir'].resolve()}")

