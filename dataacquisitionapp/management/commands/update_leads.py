from django.core.management.base import BaseCommand
from django.conf import settings
from time import sleep
import logging

from clientbx24.requests import Bitrix24
from dataacquisitionapp.tasks.lead import create_lead, create_leads


class Command(BaseCommand):
    help = 'Update all LEADS in DB'
    method = 'crm.lead.list'
    fields = ['ID', 'TITLE', 'DATE_CREATE', 'DESIGNER', 'ASSIGNED_BY_ID', 'STATUS_ID', 'SOURCE_ID', 'STATUS_SEMANTIC_ID']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bx24 = Bitrix24()
        self.logger = logging.getLogger("CommandUpdateLeads")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler("logs/commands/update_leads.log")
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def handle(self, *args, **kwargs):
        try:
            self.get_data()
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")

    def get_data(self):
        count = 0
        start_id = 0
        while True:
            params = {
                'filter': {'>ID': start_id},
                'order': {"ID": "ASC"},
                'select': self.fields,
                'start': -1
            }
            response = self.bx24.call(self.method, params)
            data_list = response.get('result', [])
            if not data_list:
                break
            for data in data_list:
                count += 1
                self.process_data(data)
            start_id = data_list[-1].get("ID")
            sleep(settings.THROTTLE)
        print("Получено или обновлено лидов: ", count)

    def process_data(self, data):
        create_lead(data)
