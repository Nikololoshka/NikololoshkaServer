from rest_framework import serializers

from .models import ScheduleCategory, ScheduleItem


class ScheduleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleCategory
        fields = ('id', 'name', 'parent', 'is_node')


class ScheduleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleItem
        fields = ('id', 'name', 'category')


class ScheduleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleItem
        fields = ('id', 'name')
