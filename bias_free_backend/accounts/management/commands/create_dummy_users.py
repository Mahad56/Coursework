from django.core.management.base import BaseCommand
from accounts.models import CustomUser 

class Command(BaseCommand):
    help = 'Create 5 dummy user accounts'

    def handle(self, *args, **kwargs):
        users = [
            {"username": "user1", "password": "password123", "email": "user1@example.com"},
            {"username": "user2", "password": "password123", "email": "user2@example.com"},
            {"username": "user3", "password": "password123", "email": "user3@example.com"},
            {"username": "user4", "password": "password123", "email": "user4@example.com"},
            {"username": "user5", "password": "password123", "email": "user5@example.com"},
        ]

        for user_data in users:
            user = CustomUser.objects.create_user(  # Use CustomUser here
                username=user_data["username"],
                password=user_data["password"],
                email=user_data["email"]
            )
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Successfully created user {user.username}"))
