from django.db import transaction
from collections import defaultdict
from datetime import datetime, timedelta
import pprint
from time import sleep
from django.conf import settings

from clientbx24.requests import Bitrix24


from dataacquisitionapp.models import (
    User,
    StageLead,
    Source,
    StatusSemanticLeads,
    Lead,
    DurationStageLead,
)


def update_stage_history(lead_ids):
    for i in range(0, len(lead_ids), settings.BATCH_SIZE):
        sleep(settings.THROTTLE)
        history_data_dict = get_stage_history_from_bx24(lead_ids[i:i + settings.BATCH_SIZE])
        for value in history_data_dict.values():
            items_list = value.get("items")
            if isinstance(items_list, list) and items_list:
                history_data_summary = analyze_lead_stage_history(items_list)
                create_history_data_list_to_db(history_data_summary)


def get_stage_history_from_bx24(ids):
    cmd = {}
    for id_ in ids:
        cmd[id_] = f"crm.stagehistory.list?entityTypeId=1&filter[OWNER_ID]={id_}&order[CREATED_TIME]=ASC"

    response = Bitrix24().call("batch", {
        "halt": 0,
        "cmd": cmd
    })

    if not response or "result" not in response or "result" not in response["result"]:
        return

    return response["result"]["result"]


def analyze_lead_stage_history(history_data_list):
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
def create_history_data_to_db(history_data):
    record = DurationStageLead.objects.filter(LEAD_ID=history_data.get("LEAD_ID"), STATUS_ID__STATUS_ID=history_data.get("STATUS_ID")).exists()
    new_data = {
        'DATE_CREATE': history_data.get('DATE_CREATE'),
        'DURATION': history_data.get('DURATION').total_seconds() / 60 if history_data.get('DURATION') else 0,
        'LEAD_ID': Lead.objects.filter(ID=history_data.get("LEAD_ID")).first(),
        'STATUS_ID': StageLead.objects.filter(STATUS_ID=history_data.get("STATUS_ID")).first(),
    }
    if record:
        res = DurationStageLead.objects.filter(LEAD_ID__ID=history_data.get("OWNER_ID"), STATUS_ID__STATUS_ID=history_data.get("STATUS_ID")).update(**new_data)
    else:
        res = DurationStageLead.objects.create(**new_data)


@transaction.atomic
def create_history_data_list_to_db(history_data):
    for data in history_data:
        create_history_data_to_db(data)
