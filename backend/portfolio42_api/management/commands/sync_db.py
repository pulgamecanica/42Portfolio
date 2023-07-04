import os
import requests
from pathlib import Path
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError

def parser_add_cache(cmd):
    cmd.add_argument('--no-cache',
                     action='store_true',
                     dest="no_cache",
                     help='If it should not cache responses from the api',
                     default=False)
    cmd.add_argument('--cache-dir',
                     action='store',
                     dest='cache_dir',
                     help='Where to store and read the cache',
                     default=Path("./cache"),
                     type=Path)

def parser_add_intra_id(cmd):
    cmd.add_argument('intra_ids',
                     nargs='*',
                     action='store',
                     help='Which intra id(s) to update',
                     metavar='intra id',
                     type=int)

def parser_add_db_command(cmd):
        parser_add_intra_id(cmd)
        parser_add_cache(cmd)

class Command(BaseCommand):
    help = "Sync the database with the intra api"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='command', required=True, metavar='sub-command')

        parser_add_db_command(subparsers.add_parser('user', help="Update user table"))
        parser_add_db_command(subparsers.add_parser('cursus', help="Update cursus table"))
        parser_add_db_command(subparsers.add_parser('project', help="Update project table"))
        parser_add_db_command(subparsers.add_parser('skill', help="Update skill table"))

        parser_add_db_command(subparsers.add_parser('relations', help="Update relations in the database"))

        cmd_clear_cache = subparsers.add_parser('clear_cache')
        cmd_clear_cache.add_argument('--cache-dir',
                                     action='store',
                                     dest='cache_dir',
                                     help='Folder of where the cache is stored',
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
        print (F"command: {options['command']}")

