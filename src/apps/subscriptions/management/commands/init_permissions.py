from django.core.management.base import BaseCommand

from apps.subscriptions import utils


class Command(BaseCommand):
    help = 'Create groups and permissions needed for subscriptions'

    def handle(self, *args, **options):
        utils.init_permissions()