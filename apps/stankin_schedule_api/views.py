import json
import zipfile
from itertools import groupby

from django.db.models import Value, IntegerField
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View
from rest_framework import views
from rest_framework.response import Response

from .models import ScheduleCategory, ScheduleVersion, SchedulePair, ScheduleItem, ScheduleUpdate
from .serializers import ScheduleCategorySerializer, ScheduleItemSerializer, ScheduleUpdateSerializer
from .utils import update_categories


class ScheduleItemView(views.APIView):
    """
    Расписание конкретной группы.
    """
    def get(self, request, pk=None):
        update = request.query_params.get('update', None)

        if update is None:
            version = ScheduleVersion.objects.filter(item=pk).order_by('update__date').first()
            pairs = SchedulePair.objects.filter(version=version)
        else:
            pairs = SchedulePair.objects.filter(version__item=pk, version__update=update)

        return Response(
            map(lambda pair: pair.to_json(), pairs)
        )


class ScheduleListView(views.APIView):
    """
    Список всех уникальных расписаний в семестре.
    """

    def get(self, request):
        category = request.query_params.get('category', None)
        if category is None:
            schedules = ScheduleItem.objects.filter(category__isnull=False)
        else:
            schedules = ScheduleItem.objects.filter(category__exact=category)

        serializer = ScheduleItemSerializer(schedules, many=True)
        return Response(serializer.data)


class ScheduleCategoriesView(views.APIView):
    """
    Расписания для данной категории.
    """

    def get(self, request):
        parent = request.query_params.get('parent', None)
        categories = ScheduleCategory.objects.filter(parent=parent)
        serializer = ScheduleCategorySerializer(categories, many=True)
        return Response(serializer.data)


class ScheduleUpdateView(views.APIView):
    """
    Версии расписания.
    """
    def get(self, request, pk=None):
        updates = ScheduleUpdate.objects.filter(update_versions__item__exact=pk) \
                                        .annotate(item=Value(pk, output_field=IntegerField())) \
                                        .values('id', 'name', 'item')[:5]
        return Response(updates)


class ScheduleInfoView(views.APIView):
    """
    Информация о репозитории с расписаниями.
    """
    def get(self, request):
        response = {
            'description': {
                'version': '2021-10-25'
            }
        }

        add_categories = request.query_params.get('categories', False)
        if add_categories:
            categories = ScheduleCategory.objects.all()
            serializer = ScheduleCategorySerializer(categories, many=True)
            response['categories'] = serializer.data

        return Response(response)


class TestView(View):
    def get(self, request):

        update_id = 21
        update = ScheduleUpdate.objects.get(id=update_id)

        response = HttpResponse(content_type='application/x-zip-compressed')
        zf = zipfile.ZipFile(response, 'w')

        dataset = SchedulePair.objects.filter(version__update__exact=update) \
            .select_related('version', 'version__item')

        print(dataset.query)

        for data in groupby(dataset, lambda x: x.version.item):
            item, pairs = data
            zf.writestr(f'{item.name}.json', json.dumps([pair.to_json() for pair in pairs], ensure_ascii=False))

        response['Content-Disposition'] = f'attachment; filename="Schedules {update.date}.zip"'

        return response


class ApiRootView(views.APIView):
    """
    REST API для расписаний МГТУ "СТАНИКИН" для
    приложения "Stankin Schedule" и "Понедельного расписания"
    """

    def get(self, request):
        # pre_populate_categories()
        # populate_schedules('../StankinSchedules/2021-05-04', 'Расписания от 4 мая 2021')
        # populate_folders('../StankinSchedules')

        # update_categories('../StankinSchedules/2021-02-15')

        # ScheduleVersion.objects.all().delete()
        # SchedulePair.objects.all().delete()

        return Response({
            'description': 'Stankin Schedule API'
        })

    def get_view_name(self):
        return "Stankin Schedule API"

    def get_view_description(self, html=False):
        if html:
            return render_to_string('schedule_api/schedule_root_api.html')

        return "REST API для расписаний МГТУ \"СТАНИКИН\" для " \
               "приложения \"Stankin Schedule\" и \"Понедельного расписания\""
