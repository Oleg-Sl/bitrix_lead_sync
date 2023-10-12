from django.db import transaction
from collections import defaultdict
from datetime import datetime, timedelta
import pprint

from dataacquisitionapp.models import (
    User,
    StageLead,
    Source,
    StatusSemanticLeads,
    Lead,
    LeadStageDuration,
)


def create_history_data_for_lead(history_data_list):
    if not history_data_list:
        return
    data_lsit = get_first_created_time(history_data_list)
    create_history_data_list(data_lsit)


def get_first_created_time(history_data_list):
    if not history_data_list:
        return
    lead_id = history_data_list[0].get("OWNER_ID")
    history_data_list.sort(key=lambda x: datetime.fromisoformat(x["CREATED_TIME"]))
    first_created_time_on_status = {}
    total_time_on_status = defaultdict(timedelta)
    previous_record = None
    for record in history_data_list:
        status_id = record["STATUS_ID"]
        created_time = datetime.fromisoformat(record["CREATED_TIME"])

        if first_created_time_on_status.get(status_id) is None:
            first_created_time_on_status[status_id] = created_time
        elif created_time < first_created_time_on_status[status_id]:
            first_created_time_on_status[status_id] = created_time

        if previous_record is not None:
            time_diff = created_time - datetime.fromisoformat(previous_record["CREATED_TIME"])
            total_time_on_status[previous_record["STATUS_ID"]] += time_diff

        previous_record = record

    result = []
    for status_id, first_time in first_created_time_on_status.items():
        total_time = total_time_on_status[status_id]
        if first_time:
            result.append({
                "LEAD_ID": lead_id,
                "STATUS_ID": status_id,
                "DATE_CREATE": first_time.strftime('%Y-%m-%dT%H:%M:%S%z'),
                # .strftime('%Y-%m-%d %H:%M:%S'),
                "DURATION": total_time,
            })

    return result


@transaction.atomic
def create_history_data(history_data):
    record = LeadStageDuration.objects.filter(LEAD_ID=history_data.get("LEAD_ID"), STATUS_ID__STATUS_ID=history_data.get("STATUS_ID")).exists()
    new_data = {
        'DATE_CREATE': history_data.get('DATE_CREATE'),
        'DURATION': history_data.get('DURATION'),
        'LEAD_ID': Lead.objects.filter(ID=history_data.get("LEAD_ID")).first(),
        'STATUS_ID': StageLead.objects.filter(STATUS_ID=history_data.get("STATUS_ID")).first(),
    }
    if record:
        res = LeadStageDuration.objects.filter(LEAD_ID__ID=history_data.get("OWNER_ID"), STATUS_ID__STATUS_ID=history_data.get("STATUS_ID")).update(**new_data)
    else:
        res = LeadStageDuration.objects.create(**new_data)


@transaction.atomic
def create_history_data_list(history_data):
    for data in history_data:
        create_history_data(data)

