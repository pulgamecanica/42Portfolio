import os
import requests
from pathlib import Path
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from portfolio42_api.models import Project
from portfolio42_api.management.api42 import Api42, ApiException

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

def update_projects(api):
    projects_returned = 1
    endpoint = '/v2/projects'

    # Api settings
    per_page = 100
    page = 0 # This will increase in the while loop

    while (projects_returned != 0):
        params = {'per_page': per_page, 'page': page}
        json = {}

        try:
            json = api.get(endpoint, params)
        except ApiException as e:
            print(f"Error: {e}")
            break

        for project in json:
            p, created = Project.objects.get_or_create(intra_id=project['id'])
            p.name = project['name'][:50]

            if (created):
                description = project['slug']
                try:
                    description = project['description']
                except:
                    pass

            p.exam = project['exam']
            p.solo = False # todo: REMOVE THIS
            p.save()
            print(f'[FETCH] fetched \'{p.name}\' ({p.intra_id})') # todo: replace this with a logger
        
        page += 1
        projects_returned = len(json)
        print(f"p: {page}, s: {projects_returned}")


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
        command = options['command']
        api = Api42(os.environ.get('INTRA_UID'), os.environ.get('INTRA_SECRET'))

        if (command == 'project' or
            command == 'skill' or
            command == 'user' or
            command == 'relations' or
            command == 'cursus'):
            match command:
                case 'project':
                    update_projects(api)

        print (F"command: {options['command']}")

