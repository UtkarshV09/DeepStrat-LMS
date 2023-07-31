import json
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    help = 'Setup data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Indicates the JSON file')

    def handle(self, *args, **options):
        with open(options['json_file']) as f:
            data = json.load(f)

            root_user_data = data['root_user']

            # Check if root user already exists
            try:
                user = User.objects.get(username=root_user_data['username'])
                self.stdout.write(
                    self.style.SUCCESS(
                        f"User '{root_user_data['username']}' already exists."
                    )
                )
            except ObjectDoesNotExist:
                # If user doesn't exist, create a new one
                User.objects.create_superuser(
                    username=root_user_data['username'],
                    password=root_user_data['password'],
                    email=root_user_data['email'],
                )
                self.stdout.write(
                    self.style.SUCCESS(f"User '{root_user_data['username']}' created.")
                )

            # setup other data
            setup_data = data['setup_data']

            # Here, you'll need to write the logic for setting up the rest of your data.
            # For now, let's just print it out.
            self.stdout.write(self.style.SUCCESS(f'Setup data: {setup_data}'))
