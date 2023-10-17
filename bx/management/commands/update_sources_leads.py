from django.core.management.base import BaseCommand
from django.conf import settings
from time import sleep
import logging

from clientbx24.requests import Bitrix24
from bx.tasks.lead_source import create_source


class Command(BaseCommand):
    help = 'Update all LEAD`S SOURCES in DB'
    method = 'crm.status.list'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bx24 = Bitrix24()
        self.logger = logging.getLogger("CommandUpdateSources")
        self.logger.setLevel(logging.INFO)
        handler = logging.handlers.TimedRotatingFileHandler("logs/commands/update_sources.log", when="midnight", interval=1, backupCount=10)
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
        params = {
            'filter': {'ENTITY_ID': 'SOURCE'},
            'order': {"ID": "ASC"},
            'start': -1
        }
        response = self.bx24.call(self.method, params)
        data_list = response.get('result', [])
        if not data_list:
            return
        for data in data_list:
            count += 1
            self.process_data(data)
        print("Создано или обновлено стадий лидов: ", count)

    def process_data(self, data):
        create_source(data)
