from django.core.management.base import BaseCommand
from kas.eboks import EboksClient


class Command(BaseCommand):
    help = 'Connects to the E-boks proxy using the current settings and prints the client configuration'

    def handle(self, *args, **options):
        client = EboksClient.from_settings()
        try:
            print(client.get_client_info().json())
        finally:
            client.close()
