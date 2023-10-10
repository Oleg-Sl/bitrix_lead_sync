from django.db import transaction
from dataacquisitionapp.models import (
    User,
    StageLead,
    Source,
    StatusSemanticLeads,
    Lead,
)


@transaction.atomic
def create_source(data_source):
    data = {
        "ID": data_source.get("ID"),
        "STATUS_ID": data_source.get("STATUS_ID"),
        "NAME": data_source.get("NAME"),
    }
    source_, created_ = Source.objects.update_or_create(ID=data_source.get("ID"), defaults=data)


@transaction.atomic
def create_objects(data_sources):
    for data_source in data_sources:
        create_source(data_source)


@transaction.atomic
def remove_objects(lead_source_remove_ids):
    Source.objects.filter(ID__in=lead_source_remove_ids).delete()
