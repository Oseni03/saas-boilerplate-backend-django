from django.conf import settings

from apps.aws_tasks.utils import lambda_task
from .models import Subscription


@lambda_task
def user_sub_post_save_task(instance):
    user_sub_instance = instance
    user = user_sub_instance.user
    subscription_obj = user_sub_instance.subscription
    groups_ids = []
    if subscription_obj is not None:
        groups = subscription_obj.groups.all()
        groups_ids = groups.values_list("id", flat=True)
    if not settings.ALLOW_CUSTOM_GROUP:
        # If user does not belong to any other type of group
        # apart from subscription groups, then set the user group only to the
        # group of the newly subscribed subscription
        user.groups.set(groups)
    else:
        # Set the user group to the combination of any other type of group the user might belong to
        # and to the newly subscribed subscription group(s)

        # To get the list of all subscription except for the newly subscribed one
        subs_qs = Subscription.objects.filter(active=True)
        if subscription_obj is not None:
            subs_qs = subs_qs.exclude(id=subscription_obj.id)
        # To get the list of group ids for each of the subscription above
        subs_groups = subs_qs.values_list("groups__id", flat=True)
        subs_groups_set = set(subs_groups)
        # groups_ids = groups.values_list("id", flat=True) # [1,2,3]
        current_groups = user.groups.all().values_list("id", flat=True)
        groups_ids_set = set(groups_ids)
        current_groups_set = set(current_groups) - subs_groups_set
        final_group_ids = list(groups_ids_set | current_groups_set)
        user.groups.set(final_group_ids)


@lambda_task
def user_sub_post_delete_task(instance):
    user_sub_instance = instance
    user = user_sub_instance.user

    # Set the user group to ther other type of group the user might belong to
    # excluding all active subscription group

    # To get the list of all active subscriptions
    subs_qs = Subscription.objects.filter(active=True)
    # To get the list of group ids for each of the subscriptions above
    subs_groups = subs_qs.values_list("groups__id", flat=True)
    subs_groups_set = set(subs_groups)
    # To get the list of group ids the user belongs to
    current_groups = user.groups.all().values_list("id", flat=True)
    final_group_ids = set(current_groups) - subs_groups_set
    user.groups.set(final_group_ids)