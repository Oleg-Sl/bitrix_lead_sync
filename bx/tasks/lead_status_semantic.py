from django.db import transaction
from bx.models import (
    User,
    StageLead,
    Source,
    StatusSemanticLeads,
    Lead,
)


@transaction.atomic
def create_status_semantic(status_semantic):
    data = {
        "STATUS_SEMANTIC_ID": status_semantic.get("STATUS_SEMANTIC_ID"),
        "STATUS_SEMANTIC_TITLE": status_semantic.get("STATUS_SEMANTIC_TITLE"),
        "TITLE": status_semantic.get("TITLE"),
    }
    status_semantic_lead, created_ = StatusSemanticLeads.objects.update_or_create(STATUS_SEMANTIC_ID=status_semantic.get("STATUS_SEMANTIC_ID"), defaults=data)
