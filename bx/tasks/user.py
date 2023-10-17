from django.db import transaction
from bx.models import (
    User,
    StageLead,
    Source,
    StatusSemanticLeads,
    Lead,
)


@transaction.atomic
def create_user(data_user):
    data = {
        "ID": data_user.get("ID"),
        "LAST_NAME": data_user.get("LAST_NAME"),
        "NAME": data_user.get("NAME"),
        "WORK_POSITION": data_user.get("WORK_POSITION"),
        "ACTIVE": data_user.get("ACTIVE"),
    }
    user, created = User.objects.update_or_create(ID=data_user.get("ID"), defaults=data)


@transaction.atomic
def create_users(data_users):
    for data_user in data_users:
        create_user(data_user)


@transaction.atomic
def remove_leads(user_remove_ids):
    User.objects.filter(ID__in=user_remove_ids).update(active=False)

