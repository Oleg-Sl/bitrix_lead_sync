from django.core.management.base import BaseCommand
from django.conf import settings
from time import sleep
import logging

from clientbx24.requests import Bitrix24
from bx.tasks.company import create_company


class Command(BaseCommand):
    help = 'Update all COMPANIES in DB'
    method = 'crm.deal.list'
    fields = ['ID', 'TITLE', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bx24 = Bitrix24()
        self.logger = logging.getLogger("CommandUpdateCompanies")
        self.logger.setLevel(logging.INFO)
        handler = logging.handlers.TimedRotatingFileHandler("logs/commands/update_companies.log", when="midnight", interval=1, backupCount=10)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def handle(self, *args, **kwargs):
        # try:
        self.get_data()
        # except Exception as e:
        #     self.logger.error(f"An error occurred: {e}")

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
        create_company(data)
