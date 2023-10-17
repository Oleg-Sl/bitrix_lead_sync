import logging
from django.core.management.base import BaseCommand

from clientbx24.events import OfflineEvents
from bx.tasks.user import create_user


class Command(BaseCommand):
    help = 'Read events - USER'
    offline_events = OfflineEvents()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("CommandEventUsers")
        self.logger.setLevel(logging.INFO)
        handler = logging.handlers.TimedRotatingFileHandler("logs/offline_events/user.log", when="midnight", interval=1, backupCount=10)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def handle(self, *args, **kwargs):
        try:
            users = self.get_data(["ONUSERADD"])
            for user in users:
                self.process_data(user)
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")

    def get_data(self, name_events):
        events_data = []
        for event_name in name_events:
            events_data += self.offline_events.get_events_data(event_name)
        return events_data

    def process_data(self, data):
        create_user(data)
