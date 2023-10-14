import os
import sys
import requests
from pathlib import Path
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from portfolio42_api.models import Project, Skill, User, Cursus, ProjectCursus, CursusUser, CursusUserSkill, CursusSkill, ProjectUser
from portfolio42_api.management.api42 import Api42, ApiException
import logging

def parser_add_db_command(cmd):
    cmd.add_argument('intra_ids',
                nargs='*',
                action='store',
                help='Which intra id(s) to update',
                metavar='intra id',
                type=int)

def update_basic(api: Api42, endpoint : str, func : callable, ids : [] = []):

    # Api settings
    per_page = 100
    page = 0 # This will increase in the while loop
    projects_returned = per_page

    params = {'per_page': per_page, 'page': page}
    if (len(ids) > 0):
        if (len(ids) > 100):
            raise ValueError()
        params['filter[id]'] = ','.join(map(str, ids))


    while (projects_returned == per_page):
        json = {}

        try:
            json = api.get(endpoint, params)
            logging.info(f"Obtained ({len(json)}) objects from api request")
        except ApiException as e:
            logging.error(e)
            break

        for obj in json:
            func(obj)

        page += 1
        params['page'] = page
        projects_returned = len(json)

        # If we are looking for specific ids we do not need to make another request
        if (len(ids) > 0):
            break

# endpoint should be formatted with `:id` which will be replaced with the actual id
def update_from_db(api : Api42, table, endpoint : str, func : callable, is_basic : bool = False, ids : [] = []):
    all = []
    if (len(ids) == 0):
        all = table.objects.all()
    else:
        all = table.objects.filter(intra_id__in=ids)
    endpoint_start = endpoint[:endpoint.index(':id')]
    endpoint_end = endpoint[endpoint.index(':id') + 3:]

    for o in all:
        ep = f"{endpoint_start}{o.intra_id}{endpoint_end}"
        try:
            json = api.get(ep)
        except ApiException as e:
            logging.error(e)
            continue

        if (is_basic):
            func(json)
        else:
            for e in json:
                func(o, e)

# Updates cursususer and cursususerskill
def update_cursususer_skill(user, cursususer):
    cu = CursusUser.update(user, cursususer)
    if (cu == None):
        return
    for i in cursususer['skills']:
        CursusUserSkill.update(cu, i)

def update_relations(api : Api42):
    update_from_db(api, Cursus, '/cursus/:id/projects', ProjectCursus.update)
    update_from_db(api, Cursus, '/cursus/:id/skills', CursusSkill.update)
    update_from_db(api, User, '/users/:id/cursus_users', update_cursususer_skill)
    update_from_db(api, User, '/users/:id/projects_users', ProjectUser.update)

def update_all(api : Api42):
    update_basic(api, '/projects', Project.update)
    update_basic(api, '/skills', Skill.update)
    update_basic(api, '/cursus', Cursus.update)
    update_from_db(api, User, '/users/:id', User.update, True)
    update_relations(api)

class Command(BaseCommand):
    help = "Sync the database with the intra api"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='command', required=True, metavar='sub-command')

        parser_add_db_command(subparsers.add_parser('user', help="Update user table"))
        parser_add_db_command(subparsers.add_parser('cursus', help="Update cursus table"))
        parser_add_db_command(subparsers.add_parser('project', help="Update project table"))
        parser_add_db_command(subparsers.add_parser('skill', help="Update skill table"))

        parser_add_db_command(subparsers.add_parser('relations', help="Update relations in the database"))
        subparsers.add_parser('all', help="Runs user, cursus, project, skill & relations")

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

        # setup logging
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

        sh = logging.StreamHandler(sys.stdout)
        log_handlers.append(sh)

        logging.basicConfig(level=log_level,
                            format=log_format,
                            datefmt=log_time_format,
                            handlers=log_handlers)

        api = Api42(os.environ.get('INTRA_UID'), os.environ.get('INTRA_SECRET'))

        match command:
            case 'project':
                update_basic(api, '/projects', Project.update, options['intra_ids'])
            case 'skill':
                update_basic(api, '/skills', Skill.update, options['intra_ids'])
            case 'cursus':
                update_basic(api, '/cursus', Cursus.update, options['intra_ids'])
            case 'user':
                update_from_db(api, User, '/users/:id', User.update, True, options['intra_ids'])
            case 'relations':
                update_relations(api)
            case 'all':
                update_all(api)

