import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from time import sleep

from dataacquisitionapp.models import (
    User,
    StageLead,
    Source,
    StatusSemanticLeads,
    Lead,
)

from dataacquisitionapp.tasks.lead_stage_history import create_history_data_for_lead
from clientbx24.requests import Bitrix24
from dataacquisitionapp.tasks.lead_stage_history import update_stage_history


class Command(BaseCommand):
    help = 'Update all LEAD`S STAGE HISOTRY in DB'
    method = 'crm.stagehistory.list'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bx24 = Bitrix24()
        self.logger = logging.getLogger("CommandUpdateStageHistory")
        self.logger.setLevel(logging.INFO)
        handler = logging.handlers.TimedRotatingFileHandler("logs/commands/update_stage_history.log", when="midnight", interval=1, backupCount=10)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def handle(self, *args, **kwargs):
        try:
            lead_ids = self.get_lead_ids()
            update_stage_history(lead_ids)
            # self.process_update_stage_history(lead_ids)
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")

    def get_lead_ids(self):
        return Lead.objects.values_list("ID", flat=True)

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
