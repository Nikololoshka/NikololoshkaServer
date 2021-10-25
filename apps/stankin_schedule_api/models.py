from django.db import models
from rest_framework import serializers


class ScheduleItem(models.Model):
    """
    Элемент расписания.
    """
    name = models.CharField(max_length=64, db_index=True, blank=False, null=False)
    category = models.ForeignKey('ScheduleCategory', on_delete=models.SET_NULL, related_name='schedules', null=True)

    def __str__(self):
        return f'ScheduleItem(name={self.name})'

    class Meta:
        managed = True
        verbose_name = 'ScheduleItem'
        verbose_name_plural = 'ScheduleItems'


class ScheduleVersion(models.Model):
    """
    Версия расписания.
    """
    item = models.ForeignKey('ScheduleItem', on_delete=models.CASCADE, related_name='versions')
    update = models.ForeignKey('ScheduleUpdate', on_delete=models.CASCADE, related_name='update_versions')

    def __str__(self):
        return f'ScheduleVersion(item={self.item.name}, update={self.update.date})'

    class Meta:
        managed = True
        verbose_name = 'ScheduleVersion'
        verbose_name_plural = 'ScheduleVersions'


class SchedulePair(models.Model):
    """
    Занятие в расписание (пара).
    """
    PAIR_TYPES = [
        ('lecture', 'Лекция'),
        ('seminar', 'Семинар'),
        ('laboratory', 'Лабораторная работа')
    ]

    PAIR_SUBGROUPS = [
        ('a', 'Подгруппа А'),
        ('b', 'Подгруппа Б'),
        ('common', 'Без подгруппы')
    ]

    version = models.ForeignKey('ScheduleVersion', on_delete=models.CASCADE, related_name='pairs')

    title = models.CharField(max_length=256, blank=False, null=False)
    lecturer = models.CharField(max_length=256, default='', blank=False, null=False)
    classroom = models.CharField(max_length=256, default='', blank=False, null=False)
    type = models.CharField(max_length=16, choices=PAIR_TYPES, blank=False, null=False)
    subgroup = models.CharField(max_length=16, choices=PAIR_SUBGROUPS, blank=False, null=False)
    time_start = models.TimeField(blank=False, null=False)
    time_end = models.TimeField(blank=False, null=False)
    dates = models.JSONField(blank=False, null=False)

    def to_json(self):
        return {
            "title": self.title,
            "lecturer": self.lecturer,
            "classroom": self.classroom,
            "subgroup": self.subgroup,
            "type": self.type,
            "time": {
                "start": self.time_start,
                "end": self.time_end
            },
            "dates": self.dates
        }

    class Meta:
        managed = True
        verbose_name = 'SchedulePair'
        verbose_name_plural = 'SchedulePairs'


class ScheduleUpdate(models.Model):
    """
    Обновление расписаний.
    """
    name = models.CharField(max_length=128, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()

    def __str__(self):
        return f'ScheduleUpdate(name={self.name}, date={self.date})'

    class Meta:
        managed = True
        verbose_name = 'ScheduleUpdate'
        verbose_name_plural = 'ScheduleUpdates'
        ordering = ['-date']


class ScheduleCategory(models.Model):
    """
    Категория расписания.
    """
    name = models.CharField(max_length=64, blank=False, null=False)
    parent = models.ForeignKey('ScheduleCategory', on_delete=models.SET_NULL,
                               related_name='children', blank=True, null=True)

    @property
    def is_node(self):
        return not self.children.exists()

    def is_category_to(self, category) -> bool:
        current_path = self
        for category_part in reversed(category):
            if category_part != current_path.name:
                return False

            current_path = current_path.parent

        return True

    def __str__(self):
        return f'ScheduleCategory(name={self.name}, parent={"root" if self.parent is None else self.parent.name})'

    class Meta:
        managed = True
        verbose_name = 'ScheduleCategory'
        verbose_name_plural = 'ScheduleCategories'
