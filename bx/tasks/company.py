from django.db import transaction


from dataacquisitionapp.models import (
    User,
    StageLead,
    Source,
    StatusSemanticLeads,
    Company,
    Lead,
)


@transaction.atomic
def create_company(data_lead):
    data = {
        "ID": data_lead.get("ID"),
        "TITLE": data_lead.get("TITLE"),
    }
    company_, created_ = Company.objects.update_or_create(ID=data_lead.get("ID"), defaults=data)
    return company_


@transaction.atomic
def create_companies(data_companies):
    for data_company in data_companies:
        create_company(data_company)


@transaction.atomic
def remove_companies(company_remove_ids):
    res = Company.objects.filter(ID__in=company_remove_ids).delete()
