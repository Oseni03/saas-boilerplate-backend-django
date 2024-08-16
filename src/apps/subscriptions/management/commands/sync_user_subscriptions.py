from sys import stdout
from typing import Any
from django.core.management.base import BaseCommand, CommandParser

from apps.subscriptions import utils


class Command(BaseCommand):
    """Can be run once a month"""

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--clear-dangling", action="store_true", default=False)

    def handle(self, *args: Any, **options: Any) -> str | None:
        # python manage.py sync_user_subs --clear-dangling
        print(options)
        clear_dangling = options.get("clear_dangling")
        if clear_dangling:
            print("Clearing dangling subs not in use active in stripe")
            utils.clear_dangling_subs()
        else:
            print("Sync active subs")
            done = utils.refresh_users_subscriptions(active_only=True)
            if done:
                print("Done")