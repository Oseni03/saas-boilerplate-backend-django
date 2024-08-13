from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

from ... import models, constants


class Command(BaseCommand):
    help = 'Create groups and permissions needed for subscriptions'

    def handle(self, *args, **options):
        for plan in constants.subscription_plan_groups:
            group, _ = Group.objects.get_or_create(name=plan.lower())
            if plan == constants.SubscriptionPlanGroups.Advance:
                group.permissions.add(
                    Permission.objects.get(codename=constants.CommomPermissions.Advance),
                    Permission.objects.get(codename=constants.CommomPermissions.Pro),
                    Permission.objects.get(codename=constants.CommomPermissions.Basic),
                )
            elif plan == constants.SubscriptionPlanGroups.Pro:
                group.permissions.add(
                    Permission.objects.get(codename=constants.CommomPermissions.Pro),
                    Permission.objects.get(codename=constants.CommomPermissions.Basic),
                )
            elif plan == constants.SubscriptionPlanGroups.Basic:
                group.permissions.add(
                    Permission.objects.get(codename=constants.CommomPermissions.Basic)
                )
            
            group.save()