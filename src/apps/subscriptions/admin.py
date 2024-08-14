from django.contrib import admin

from .models import Subscription, UserSubscription, SubscriptionPrice


class SubscriptionPriceInline(admin.TabularInline):
    model = SubscriptionPrice
    readonly_fields = ["stripe_id"]
    can_delete = False
    extra = 0


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["name", "active"]
    list_editable = ["active"]
    readonly_fields = ["stripe_id", "created", "updated"]

    inlines = [SubscriptionPriceInline]

# Register your models here.
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(UserSubscription)