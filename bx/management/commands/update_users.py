from django.core.management.base import BaseCommand
from django.conf import settings
from time import sleep
import logging

from clientbx24.requests import Bitrix24
from bx.tasks.user import create_user


class Command(BaseCommand):
    help = 'Update all USER in DB'
    method = 'user.get'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bx24 = Bitrix24()
        self.logger = logging.getLogger("CommandUpdateUsers")
        self.logger.setLevel(logging.INFO)
        handler = logging.handlers.TimedRotatingFileHandler("logs/commands/update_users.log", when="midnight", interval=1, backupCount=10)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def handle(self, *args, **kwargs):
        try:
            self.get_users_data()
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")

    def get_users_data(self):
        count = 0
        start_user_id = 0
        while True:
            params = {
                "filter": {'>ID': start_user_id},
                "order": {"ID": "ASC"},
                "start": -1
            }
            response = self.bx24.call(self.method, params)
            users_list = response.get('result', [])
            if not users_list:
                break
            for user in users_list:
                count += 1
                self.process_user_data(user)
            start_user_id = users_list[-1].get("ID")
            sleep(settings.THROTTLE)
        print("Добавлено или обновлено пользователей: ", count)

    def process_user_data(self, user_data):
        create_user(user_data)
