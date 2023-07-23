import os
import sys
import requests
from pathlib import Path
from datetime import datetime, timedelta
from django.utils import timezone
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

def update_db(api: Api42, endpoint : str, func : callable, ids : [] = []):

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
            logging.error(f"Error on 42 API request")
            break

        for obj in json:
            func(obj)
        
        page += 1
        params['page'] = page
        projects_returned = len(json)

        # If we are looking for specific ids we do not need to make another request
        if (len(ids) > 0):
            break

def update_project(project):
    p, created = Project.objects.get_or_create(intra_id=project['id'])
    
    p.name = project['name'][:50]
    if (created):
        
        try:
            p.description = project['description']
        except:
            p.description = project['slug']

    p.exam = project['exam']
    p.solo = False # todo: REMOVE THIS
    p.save()

    if (created):
        logging.info(f"Created new project: {p.name} (id: {p.id}, intra_id: {p.intra_id})")
    else:
        logging.info(f"Refreshed project: {p.name} (id: {p.id}, intra_id: {p.intra_id})")
    logging.debug(f"Updated project ({p.id}) with: intra_id={p.intra_id}, desc={p.description}, exam={p.exam}")

def update_skill(skill):
    s, created = Skill.objects.get_or_create(intra_id=skill['id'])
    
    s.name = skill['name'][:100]
    s.save()

    if (created):
        logging.info(f"Created new skill: {s.name} (id: {s.id}, intra_id: {s.intra_id})")
    else:
        logging.info(f"Refreshed skill: {s.name} (id: {s.id}, intra_id: {s.intra_id})")
    logging.debug(f"Updated skill ({s.id}) with: intra_id={s.intra_id}, name={s.name}")

def update_cursus(cursus):
    c, created = Cursus.objects.get_or_create(intra_id=cursus['id'])
    
    c.name = cursus['name'][:50]
    c.kind = cursus['kind'][:50]
    c.save()

    if (created):
        logging.info(f"Created new cursus: {c.name} (id: {c.id}, intra_id: {c.intra_id})")
    else:
        logging.info(f"Refreshed cursus: {c.name} (id: {c.id}, intra_id: {c.intra_id})")
    logging.debug(f"Updated cursus ({c.id}) with: intra_id={c.intra_id}, name={c.name}, kind={c.kind}")

def update_users(api : Api42, ids : [] = []):
    per_req = 100 # Amount of users to request
    users = User.objects.all()
    if (len(ids) > 0):
        users = User.objects.filter(intra_id__in=ids)

    i = 0
    total = users.count()
    while (i < total):
        end_i = min(i + per_req, total)
        user_batch = users[i:end_i]
        params = { 'filter[id]': (','.join(map(lambda u : str(u.intra_id), user_batch)))}
        r = api.get('/v2/users', params)

        logging.info(f"Obtained ({len(r)}) users from api request")

        for u_json in r:
            intra_id = u_json['id']
            u = User.objects.get(intra_id=intra_id)

            u.intra_username = u_json['login']
            u.first_name = u_json['first_name']
            u.last_name = u_json['last_name']
            u.email = u_json['email']
            u.intra_url = u_json['url']
            u.image_url = u_json['image']['link']

            u.save()

            logging.info(f"Refreshed user: {u.intra_username} (id: {u.id}, intra_id: {u.intra_id})")

        i += per_req

def update_projectcursus(cursus, project):
    p = Project.objects.get(intra_id=project['id'])
    cp, created = ProjectCursus.objects.get_or_create(id_project=p, id_cursus=cursus)
    cp.save()

    if (created):
        logging.info(f"Created new projectcursus: (project_id: {cp.id_project}, cursus_id: {cp.id_cursus})")
    else:
        logging.info(f"Refreshed projectcursus: (project_id: {cp.id_project}, cursus_id: {cp.id_cursus})")

# Updates cursususer and cursususerskill
def update_cursususer_skill(user, cursususer):
    c = Cursus.objects.get(intra_id=cursususer['cursus']['id'])
    cu, created = CursusUser.objects.get_or_create(intra_id=cursususer['id'],
                                                   id_user=user,
                                                   id_cursus=c,
                                                   defaults={'level': cursususer['level'],
                                                             'begin_at': cursususer['begin_at'][:10]})
    cu.level = cursususer['level']
    cu.save()

    if (created):
        logging.info(f"Created new cursususer: (cursus_id: {cu.id_cursus}, user_id: {cu.id_user})")
    else:
        logging.info(f"Refreshed cursususer: (cursus_id: {cu.id_cursus}, user_id: {cu.id_user})")

    for i in cursususer['skills']:
        s = Skill.objects.get(intra_id=i['id'])
        cs = CursusSkill.objects.get(id_cursus=c, id_skill=s)
        cus, created = CursusUserSkill.objects.get_or_create(id_cursus_user=cu,
                                                    id_cursus_skill=cs,
                                                    defaults={'level': i['level']})
        cus.level = i['level']
        cus.save()

        if (created):
            logging.info(f"Created new cursususer: (cursus: {cus.id_cursus_skill}, user: {cus.id_cursus_user})")
        else:
            logging.info(f"Refreshed cursususer: (cursus: {cus.id_cursus_skill}, user: {cus.id_cursus_user})")

def update_projectuser(user, projectuser):
    p = Project.objects.get(intra_id=projectuser['project']['id'])
    pu, created = ProjectUser.objects.get_or_create(intra_id=projectuser['id'],
                                           id_user=user,
                                           id_project=p,
                                           defaults={'finished_at': datetime(1,1,1,0,0),
                                                     'finished': False,
                                                     'grade': 0})
    pu.finished = projectuser['validated?'] if projectuser['validated?'] is not None else False
    if pu.finished:
        d = timezone.make_aware(datetime.strptime(projectuser['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ'), timezone.utc)
        pu.finished_at = d
    pu.grade = projectuser['final_mark'] if projectuser['final_mark'] is not None else 0
    pu.save()
    
    if (created):
        logging.info(f"Created new cursususer: (user: {pu.id_user}, project: {pu.id_project})")
    else:
        logging.info(f"Refreshed cursususer: (user: {pu.id_user}, project: {pu.id_project})")

    
def update_cursusskill(cursus, skill):
    s = Skill.objects.get(intra_id=skill['id'])
    cs, created = CursusSkill.objects.get_or_create(id_cursus=cursus, id_skill=s)
    cs.save()

    if (created):
        logging.info(f"Created new cursusSkill: (cursus_id: {cs.id_cursus}, skill_id: {cs.id_skill})")
    else:
        logging.info(f"Refreshed cursusSkill: (cursus_id: {cs.id_cursus}, skill_id: {cs.id_skill})")


# endpoint should be formatted with `:id` which will be replaced with the actual id
def update_from_db(api : Api42, table, endpoint : str, func : callable):
    all = table.objects.all()
    endpoint_start = endpoint[:endpoint.index(':id')]
    endpoint_end = endpoint[endpoint.index(':id') + 3:]

    for o in all:
        ep = f"{endpoint_start}{o.intra_id}{endpoint_end}"
        json = api.get(ep)
        for e in json:
            func(o, e)

def update_relations(api : Api42):
    update_from_db(api, Cursus, '/v2/cursus/:id/projects', update_projectcursus)
    update_from_db(api, Cursus, '/v2/cursus/:id/skills', update_cursusskill)
    update_from_db(api, User, '/v2/users/:id/cursus_users', update_cursususer_skill)
    update_from_db(api, User, '/v2/users/:id/projects_users', update_projectuser)

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
        sh.setFormatter(logging.Formatter(log_format))
        log_handlers.append(sh)


        logging.basicConfig(level=log_level,
                            format=log_format,
                            datefmt=log_time_format,
                            handlers=log_handlers)

        api = Api42(os.environ.get('INTRA_UID'), os.environ.get('INTRA_SECRET'))

        match command:
            case 'project':
                update_db(api, '/v2/projects', update_project, options['intra_ids'])
            case 'skill':
                update_db(api, '/v2/skills', update_skill, options['intra_ids'])
            case 'cursus':
                update_db(api, '/v2/cursus', update_cursus, options['intra_ids'])
            case 'user':
                update_users(api, options['intra_ids'])
            case 'relations':
                update_relations(api)

