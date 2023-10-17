from django.core.management.base import BaseCommand
from django.conf import settings
from time import sleep
import logging

from clientbx24.events import OfflineEvents
from clientbx24.requests import Bitrix24

from bx.tasks.company import create_company, remove_companies


class Command(BaseCommand):
    help = 'Read events - Company'
    method = 'crm.company.get'
    offline_events = OfflineEvents()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bx24 = Bitrix24()
        self.logger = logging.getLogger("CommandEventCompanies")
        self.logger.setLevel(logging.INFO)
        handler = logging.handlers.TimedRotatingFileHandler("logs/offline_events/company.log", when="midnight", interval=1, backupCount=10)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def handle(self, *args, **kwargs):
        # try:
        company_update_ids = self.get_company_ids(["ONCRMCOMPANYADD", "ONCRMCOMPANYUPDATE"])
        company_remove_ids = self.get_company_ids(["ONCRMCOMPANYDELETE"])
        self.process_company_ids(company_update_ids)
        self.remove_company(company_remove_ids)
        # except Exception as e:
        #     self.logger.error(f"An error occurred: {e}")

    def get_company_ids(self, name_events):
        company_ids = []
        for event_name in name_events:
            company_ids += [item.get("FIELDS", {}).get("ID") for item in self.offline_events.get_events_data(event_name)]
        return company_ids

    def process_company_ids(self, company_ids):
        for i in range(0, len(company_ids), settings.BATCH_SIZE):
            # try:
            data_companies = self.get_company_data(company_ids[i:i + settings.BATCH_SIZE])
            create_company(data_companies.values())
            # except Exception as e:
            #     self.logger.error(f"An error occurred: {e}. Companies ids: {', '.join(company_ids[i:i + settings.BATCH_SIZE])}")
            sleep(settings.THROTTLE)

    def remove_company(self, company_remove_ids):
        remove_companies(company_remove_ids)

    def get_company_data(self, ids):
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

