from django.contrib import admin
from apt.models import Apt_list, Apt_detail, Apt_purchase, Apt_jeonse,  Apt_ratio, Location


# Register your models here.

@admin.register(Apt_list)
class Apt_list(admin.ModelAdmin):
    pass


@admin.register(Apt_detail)
class Apt_detail(admin.ModelAdmin):
    pass

@admin.register(Apt_purchase)
class Apt_purchase(admin.ModelAdmin):
    pass


@admin.register(Apt_jeonse)
class Apt_jeonse(admin.ModelAdmin):
    pass

# @admin.register(Apt_max)
# class Apt_max(admin.ModelAdmin):
#     pass

@admin.register(Apt_ratio)
class Apt_ratio(admin.ModelAdmin):
    pass

@admin.register(Location)
class Location(admin.ModelAdmin):
    pass