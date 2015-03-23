from django.core.management.base import BaseCommand, CommandError
from its.users.models import User

class Command(BaseCommand):
    args = 'None'
    help = 'Adds a user as an administrator.'

    def handle(self, *args, **options):
        
        first = input("Enter your first name: ") 
        last = input("Enter your last name: ")
        new_email = input("Enter your email address: ")
        odin = input("Enter your ODIN username: ")

        try:
            new_user = User(first_name = first, last_name = last, email = new_email, username = odin, is_active=True, is_staff=True)
            new_user.save()
            
        except Exception as e:
            self.stdout.write('Unable to add user!')

        self.stdout.write('Successfully added admin user!')