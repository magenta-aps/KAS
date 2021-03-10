from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = 'Creates or updates user for REST communication from selvbetjening'

    def add_arguments(self, parser):
        parser.add_argument('token_value', type=str)

    def handle(self, *args, **options):
        token_value = options['token_value']
        print(f"Create/update rest user with token {token_value}")
        user, c = User.objects.get_or_create(username='rest')
        try:
            # 'key' is the pk of the Token model, so we cannot update it
            token = Token.objects.get(user=user)
            if token.key != token_value:
                print("Token changed, deleting and recreating")
                token.delete()
                Token.objects.create(user=user, key=token_value)
            else:
                print("Token unchanged")
        except Token.DoesNotExist:
            print("Token does not exist, creating")
            Token.objects.create(user=user, key=token_value)

