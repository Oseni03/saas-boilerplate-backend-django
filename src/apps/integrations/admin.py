from django.contrib import admin
from .models import Thirdparty, Integration

# Register your models here.
@admin.register(Thirdparty)
class ThirdpartyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active')


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'thirdparty', 'is_active', 'access_revoked')