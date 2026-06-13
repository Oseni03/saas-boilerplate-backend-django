from typing import Any
from django.core.management.base import BaseCommand

from apps.subscriptions import utils


class Command(BaseCommand):
    """A command to sync subscription groups and permissions.
    
    This command should be run after creating different subscriptions and defining 
    their associated groups and permissions.
    """
    
    def handle(self, *args: Any, **options: Any) -> str | None:
        utils.sync_subs()