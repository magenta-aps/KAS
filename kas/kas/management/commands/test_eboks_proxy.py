from django.core.management.base import BaseCommand

from kas.eboks import EboksClient


class Command(BaseCommand):
    help = "Connects to E-boks proxy using current settings and prints configuration"

    def handle(self, *args, **options):
        client = EboksClient.from_settings()
        try:
            print(client.get_client_info().json())
        finally:
            client.close()
