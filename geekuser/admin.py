from django.contrib import admin
from .models import GeekUser
# Register your models here.
@admin.register(GeekUser)
class GeekUserAdmin(admin.ModelAdmin):
    list_display = ('username','invation_code', 'par_invation_code','sub_invation_code')
    ordering = ('id',)