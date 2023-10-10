from django.db import transaction
from dataacquisitionapp.models import (
    User,
    StageLead,
    Source,
    StatusSemanticLeads,
    Lead,
)


@transaction.atomic
def create_lead(data_lead):
    data = {
        "ID": data_lead.get("ID"),
        "TITLE": data_lead.get("TITLE"),
        "DATE_CREATE": data_lead.get("DATE_CREATE"),
        "ASSIGNED_BY_ID": User.objects.filter(ID=data_lead.get("ASSIGNED_BY_ID")).first(),
        "STATUS_ID": StageLead.objects.filter(STATUS_ID=data_lead.get("STATUS_ID")).first(),
        "SOURCE_ID": Source.objects.filter(STATUS_ID=data_lead.get("SOURCE_ID")).first(),
        "STATUS_SEMANTIC_ID": StatusSemanticLeads.objects.filter(STATUS_SEMANTIC_ID=data_lead.get("STATUS_SEMANTIC_ID")).first(),
    }
    lead_, created_ = Lead.objects.update_or_create(ID=data_lead.get("ID"), defaults=data)
    return lead_


@transaction.atomic
def create_leads(data_leads):
    for data_lead in data_leads:
        create_lead(data_lead)


@transaction.atomic
def remove_leads(lead_remove_ids):
    res = Lead.objects.filter(ID__in=lead_remove_ids).delete()
