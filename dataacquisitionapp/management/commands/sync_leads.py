from django.core.management.base import BaseCommand
from django.conf import settings
from time import sleep
import logging

from clientbx24.events import OfflineEvents
from clientbx24.requests import Bitrix24
from dataacquisitionapp.tasks.lead import create_leads, remove_leads
from dataacquisitionapp.tasks.lead_stage_history import create_history_data_for_lead

from dataacquisitionapp.tasks.lead_stage_history import process_update_stage_history


class Command(BaseCommand):
    help = 'Read events - LEAD'
    method = 'crm.lead.get'
    offline_events = OfflineEvents()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bx24 = Bitrix24()
        self.logger = logging.getLogger("CommandEventLeads")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler("logs/offline_events/lead.log")
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def handle(self, *args, **kwargs):
        try:
            lead_update_ids = self.get_lead_ids(["ONCRMLEADADD", "ONCRMLEADUPDATE"])
            print("lead_update_ids = ", lead_update_ids)
            lead_remove_ids = self.get_lead_ids(["ONCRMLEADDELETE"])
            print("lead_remove_ids = ", lead_remove_ids)
            self.process_lead_ids(lead_update_ids)
            self.remove_leads(lead_remove_ids)
            process_update_stage_history(lead_update_ids)
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")

    def get_lead_ids(self, name_events):
        lead_ids = []
        for event_name in name_events:
            lead_ids += [item.get("FIELDS", {}).get("ID") for item in self.offline_events.get_events_data(event_name)]
        return lead_ids

    def process_lead_ids(self, lead_ids):
        for i in range(0, len(lead_ids), settings.BATCH_SIZE):
            try:
                data_leads = self.get_lead_data(lead_ids[i:i + settings.BATCH_SIZE])
                create_leads(data_leads.values())
            except Exception as e:
                self.logger.error(f"An error occurred: {e}. Lead ids: {', '.join(lead_ids[i:i + settings.BATCH_SIZE])}")
            sleep(settings.THROTTLE)

    def remove_leads(self, lead_remove_ids):
        remove_leads(lead_remove_ids)

    def get_lead_data(self, ids):
        cmd = {}
        for id_ in ids:
            cmd[id_] = f"{self.method}?id={id_}"

        response = self.bx24.call("batch", {
            "halt": 0,
            "cmd": cmd
        })
        if not response or "result" not in response or "result" not in response["result"]:
            return

        return response["result"]["result"]

    # def process_update_stage_history(self, lead_ids):
    #     for i in range(0, len(lead_ids), settings.BATCH_SIZE):
    #         try:
    #             history_data_dict = self.get_stage_history_lead_data(lead_ids[i:i + settings.BATCH_SIZE])
    #             self.process_data(history_data_dict)
    #         except Exception as e:
    #             self.logger.error(f"An error occurred: {e}.")
    #         sleep(settings.THROTTLE)
    #
    # def get_stage_history_lead_data(self, ids):
    #     cmd = {}
    #     for id_ in ids:
    #         cmd[id_] = f"{self.method}?entityTypeId=1&filter[OWNER_ID]={id_}&order[CREATED_TIME]=ASC"
    #
    #     response = self.bx24.call("batch", {
    #         "halt": 0,
    #         "cmd": cmd
    #     })
    #
    #     if not response or "result" not in response or "result" not in response["result"]:
    #         return
    #
    #     return response["result"]["result"]
    #
    # def process_data(self, history_data_dict):
    #     for value in history_data_dict.values():
    #         items_list = value.get("items")
    #         if isinstance(items_list, list):
    #             create_history_data_for_lead(items_list)
    #
