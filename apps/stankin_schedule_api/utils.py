import datetime
import json
import os
from pathlib import Path

from .models import ScheduleCategory, ScheduleItem, ScheduleUpdate, ScheduleVersion, SchedulePair


def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


def find_category(categories, category_parts):
    for category in categories:
        if category.is_category_to(category_parts):
            return category

    return None


def pre_populate_categories():
    with open('./resources/categories.json', 'r', encoding='utf-8') as file:
        categories = json.load(file)

        for category in categories:
            print(category)
            pre_populate_category(category['children'], category['name'], None)


def pre_populate_category(categories, name, parent):
    new_category = ScheduleCategory.objects.create(name=name, parent=parent)
    for category in categories:
        pre_populate_category(category['children'], category['name'], new_category)


def populate_folders(folder):
    folder_path = Path(folder).absolute().resolve()
    categories = list(ScheduleCategory.objects.all())

    for item_path in folder_path.iterdir():
        if item_path.is_dir():
            date = datetime.datetime.strptime(item_path.stem.split(' ')[0], '%Y-%m-%d')
            print(f'Import:', item_path)
            populate_schedules(item_path, categories, date)


def populate_schedules(folder_path, categories, date):
    schedule_update, _ = ScheduleUpdate.objects.get_or_create(
        name=f'Расписания от {date.strftime("%d.%m.%Y")}',
        date=date
    )

    for dir_path, _, filenames in os.walk(folder_path):
        for filename in filenames:
            schedule_name = Path(filename).stem
            print(f'\tImport {schedule_name}')

            schedule_item = get_or_none(ScheduleItem, name=schedule_name)

            if schedule_item is None:
                current_path = Path(dir_path).resolve().relative_to(folder_path)
                category = find_category(categories, current_path.parts)

                if category is None:
                    print('Category not found:', schedule_name)

                schedule_item = ScheduleItem.objects.create(
                    name=schedule_name,
                    category=category
                )

            schedule_version, created = ScheduleVersion.objects.get_or_create(item=schedule_item,
                                                                              update=schedule_update)
            if not created:
                continue

            with open(dir_path + os.sep + filename, 'r', encoding='utf-8') as file:

                SchedulePair.objects.bulk_create(
                    [
                        SchedulePair(
                            version=schedule_version,
                            title=pair['title'],
                            lecturer=pair['lecturer'],
                            classroom=pair['classroom'],
                            type=pair['type'].lower(),
                            subgroup=pair['subgroup'].lower(),
                            time_start=pair['time']['start'],
                            time_end=pair['time']['end'],
                            dates=pair['dates']
                        )
                        for pair in json.load(file)
                    ]
                )


def update_categories(folder):
    folder_path = Path(folder).absolute().resolve()
    categories = list(ScheduleCategory.objects.all())

    count = 0
    for dir_path, _, filenames in os.walk(folder_path):
        for filename in filenames:
            current_path = Path(dir_path).resolve().relative_to(folder_path)
            category = find_category(categories, current_path.parts)

            if category is not None:
                count += 1
                schedule_name = Path(filename).stem
                ScheduleItem.objects.filter(name=schedule_name).update(category=category)

    return count
