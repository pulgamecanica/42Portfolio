import os
import requests
from pathlib import Path
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from portfolio42_api.models import Project

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

class IntraAuth():
    token_path = 'https://api.intra.42.fr/oauth/token'
    
    def __init__(self):
        self.uid = os.environ.get('INTRA_UID')
        self.secret = os.environ.get('INTRA_SECRET')

        self.token_expires = datetime(1, 1, 1)
        self.access_token = None

    def token(self):
        # If the token has expired or its not available try to refresh token
        if (self.token_expires > datetime.now() and self.access_token is not None):
            return self.access_token

        data = {
            'grant_type': 'client_credentials',
            'client_id': self.uid,
            'client_secret': self.secret
        }

        # Fetch token
        res = requests.post(IntraAuth.token_path, data=data)
        json = res.json()

        if (res.status_code != 200):
            raise RuntimeError(res.json()['error_description'])

        # Extract info from response
        self.access_token = json['access_token']
        self.token_expires = datetime.now() + timedelta(seconds=json['expires_in'])

        print (f"[INFO][TOKEN] fetched new token, expires at: {self.token_expires}")
        return self.access_token

def update_projects(auth):
    projects_returned = 1
    base_url = 'https://api.intra.42.fr/v2/'
    endpoint = 'projects'
    
    headers = {'Authorization': f"Bearer {auth.token()}"}

    # Api settings
    per_page = 100
    page = 0 # This will increase in the while loop

    while (projects_returned != 0):
        params = {'per_page': per_page, 'page': page}
        res = requests.get('https://api.intra.42.fr/v2/projects', headers=headers, params=params)
        if (res.status_code != 200):
            print(res.text)
            raise CommandError("[FETCH][PROJECT] Trouble fetching projects")

        json = res.json()

        for project in res.json():
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
            page += 1
            print(f'[FETCH] fetched \'{p.name}\' ({p.intra_id})') # todo: replace this with a logger
        


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
        auth = IntraAuth()

        if (command == 'project' or
            command == 'skill' or
            command == 'user' or
            command == 'relations' or
            command == 'cursus'):
            auth = IntraAuth()
            match command:
                case 'project':
                    update_projects(auth)

        print (F"command: {options['command']}")

