from django.urls import re_path

from .views import ApiRootView, ScheduleListView, ScheduleItemView,\
    ScheduleCategoriesView, ScheduleUpdateView, ScheduleInfoView, TestView


urlpatterns = [
    re_path(r'^v0/?$', ApiRootView.as_view(), name='schedule-api-root'),
    re_path(r'^v0/info/?$', ScheduleInfoView.as_view(), name='schedule-api-info'),
    re_path(r'^v0/schedules/?$', ScheduleListView.as_view(), name='schedule-api-list'),
    re_path(r'^v0/schedules/(?P<pk>\d+)/?$', ScheduleItemView.as_view(), name='schedule-api-item'),
    re_path(r'^v0/categories/?$', ScheduleCategoriesView.as_view(), name='schedule-api-category'),
    re_path(r'^v0/updates/(?P<pk>\d+)/?$', ScheduleUpdateView.as_view(), name='schedule-api-update'),

    re_path(r'^v0/test/?$', TestView.as_view(), name='schedule-api-test')
]
