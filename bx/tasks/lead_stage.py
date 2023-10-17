from django.db import transaction
from dataacquisitionapp.models import (
    User,
    StageLead,
    Source,
    StatusSemanticLeads,
    Lead,
)


@transaction.atomic
def create_stage(data_stage):
    data = {
        "ID": data_stage.get("ID"),
        "STATUS_ID": data_stage.get("STATUS_ID"),
        "NAME": data_stage.get("NAME"),
    }
    stage_, created_ = StageLead.objects.update_or_create(ID=data_stage.get("ID"), defaults=data)


@transaction.atomic
def create_stages(data_stages):
    for data_stage in data_stages:
        create_stage(data_stage)


@transaction.atomic
def remove_stages(lead_stage_remove_ids):
    StageLead.objects.filter(ID__in=lead_stage_remove_ids).delete()

