from django.contrib import admin, messages

# Register your models here.
from django.utils.translation import ngettext

from .models import ScheduleItem, ScheduleCategory, ScheduleVersion, ScheduleUpdate, SchedulePair
from .utils import update_categories


@admin.register(ScheduleItem)
class ScheduleItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')


@admin.register(SchedulePair)
class SchedulePairAdmin(admin.ModelAdmin):
    list_display = ('id', 'version', 'title', 'lecturer', 'classroom', 'type', 'subgroup', 'time_start', 'time_end')


@admin.register(ScheduleVersion)
class ScheduleVersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'update')


@admin.register(ScheduleCategory)
class ScheduleCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent')


@admin.register(ScheduleUpdate)
class ScheduleUpdateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date')
    list_filter = ('date',)

    # actions = ['update_categories']

    # @admin.action(description='Обновить категории расписаний', permissions=['change'])
    # def update_categories(self, request, queryset):
    #
    #     count = update_categories('../StankinSchedules/2021-03-01')
    #
    #     self.message_user(request, ngettext(
    #         '%d категория расписания была изменена.',
    #         '%d категорий расписаний были изменены.',
    #         count,
    #     ) % count, messages.SUCCESS)
