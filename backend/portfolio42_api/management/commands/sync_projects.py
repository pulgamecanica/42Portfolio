import os
import requests
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from portfolio42_api.models import Project


class Command(BaseCommand):
    help = "Projects Sync with INTR API"

    print("Starting Now", datetime.now())

    # Validation is called explicitly each time the server is reloaded.
    stealth_options = ("shutdown_message",) # What is this?

    def handle(self, *args, **options):
        # Intra API endpoint which returns the projects
        ENDPOINT = "https://api.intra.42.fr/v2/projects"

        # Intra API let's you sort the projects by
        sort = "name"

        # Intra API let's you limit the number of projects returned to 
        # relieve the json overload with a maximum limit of 100
        elements_per_page = 100

        # Intra API pagination
        page = 1

        """
         Create a CronJob Object and save it to the DB
         status, type, start_time, end_time, duration, logfile
         The CronJob object is created, and the following attributes are assigned:
         status: false by default
         type: Project Intra Sync
         start_time: datetime.now()
         end_time: NULL
         duration: 0
         logfile: project_log_day_month_year.log
        """

        """
        Encapsulate this in a base method to be recycled
        by all other commands trying to get an intra token
        """
        get_token_path = "https://api.intra.42.fr/oauth/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id':  os.environ.get('INTRA_UID'),
            'client_secret': os.environ.get('INTRA_SECRET'),
        }
        r = requests.post(get_token_path, data=data)

        """
            Check if request was succesfull, if not,
            return an error Response with the reason
        """
        if (r.status_code != 200):
            raise CommandError("[Get Token Error]: Check your credentials, the api returned [%d]" % r.status_code);

        # Generate Headers for the projects request
        try:
            token = r.json()['access_token']
            headers = {"Authorization": "Bearer %s" % token}
        except:
            raise CommandError("[Get Token Error]: JSON response is different from expected");
    
        # Request all projects, iterating each page from INTRA
        projects_returned = 1
        while (projects_returned != 0):
            params = {"sort": sort, "per_page": elements_per_page, "page": page}
            r = requests.get(ENDPOINT, headers = headers, params = params)
            if (r.status_code != 200):
                raise CommandError("[Sync Projects]: Failed to load Projects from the intra API [%d]" % r.status_code);
            # Verify that intra is actually returning the expected list
            if not isinstance(r.json(), list):
                raise CommandError("[Sync Projects]: JSON response is different from expected");
            # Returns an array of project objects
            for project in r.json():
                description = project['slug']
                try:
                    description = project['description']
                except:
                    pass
                p, created = Project.objects.get_or_create(intra_id = project['id'])
                p.name = project['name'][:50]
                if created:
                    p.description = description
                p.exam = project['exam']
                p.solo = False
                p.save()
                print(project['id'], "%s" % "Created" if created else "Updated")
                # Write to the logfile the change
                # If create, then logfile says its created
                # Else just updated
            page += 1
            projects_returned = len(r.json())

            # Create log file and upadte the con Job information
        print("Ending Now", datetime.now())