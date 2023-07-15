import os
import sys
import requests
from pathlib import Path
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from portfolio42_api.models import Project
from portfolio42_api.management.api42 import Api42, ApiException
import logging

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

def update_projects(api, logger):
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
            logger.info(f"Obtained ({len(json)}) projects from api request")
        except ApiException as e:
            logger.error(f"Error on 42 API request")
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
            if (created):
                logger.info(f"Created new project: {p.name} (id: {p.id}, intra_id: {p.intra_id})")
            else:
                logger.info(f"Refreshed project: {p.name} (id: {p.id}, intra_id: {p.intra_id})")
        
        page += 1
        projects_returned = len(json)


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
                            dest="no_logfile",
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

        # setup logger
        log_level = options['verbosity'] * 10
        log_format = "[%(asctime)s][%(levelname)s] %(message)s"
        log_time_format = "%y%m%d%H%M%S"
        log_handlers = []
        if (log_level > 0):
            if (not options['no_logfile']):
                log_dir : Path = options['log_dir']
                log_dir.mkdir(parents=True, exist_ok=True)
                logfile_name = f"{datetime.now().strftime('%y%m%d%H%M%S')}_{command}.log"
                handler = logging.FileHandler(f"{log_dir.absolute()}/{logfile_name}")
                log_handlers.append(handler)
        else:
            log_level = 0

        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(logging.Formatter(log_format))
        log_handlers.append(sh)


        logging.basicConfig(level=log_level,
                            format=log_format,
                            datefmt=log_time_format,
                            handlers=log_handlers)
        logger = logging.getLogger('api')

        api = Api42(os.environ.get('INTRA_UID'), os.environ.get('INTRA_SECRET'), logger=logger)

        if (command == 'project' or
            command == 'skill' or
            command == 'user' or
            command == 'relations' or
            command == 'cursus'):
            match command:
                case 'project':
                    update_projects(api, logger)

        print (F"command: {options['command']}")

