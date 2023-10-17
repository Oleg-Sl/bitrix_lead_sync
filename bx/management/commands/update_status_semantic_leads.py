from django.core.management.base import BaseCommand
import logging

from bx.tasks.lead_status_semantic import create_status_semantic


class Command(BaseCommand):
    help = 'Update all LEAD`S STATUS SEMANTICS in DB'
    data_list = [
        {'STATUS_SEMANTIC_ID': 'F', 'STATUS_SEMANTIC_TITLE': 'failed',     'TITLE': 'обработан неуспешно'},
        {'STATUS_SEMANTIC_ID': 'S', 'STATUS_SEMANTIC_TITLE': 'success',    'TITLE': 'обработан успешно'},
        {'STATUS_SEMANTIC_ID': 'P', 'STATUS_SEMANTIC_TITLE': 'processing', 'TITLE': 'лид в обработке'},
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("CommandUpdateStatusSemantic")
        self.logger.setLevel(logging.INFO)
        handler = logging.handlers.TimedRotatingFileHandler("logs/commands/update_status_semancic_lead.log", when="midnight", interval=1, backupCount=10)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def handle(self, *args, **kwargs):
        try:
            for data in self.data_list:
                self.process_data(data)
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")

    def process_data(self, data):
        create_status_semantic(data)
