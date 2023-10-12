import os
import json
from django.conf import settings


path_secret_file = os.path.join(settings.BASE_DIR, 'clientbx24', 'secrets_bx24.json')


# def save_secrets(data):
#     """ Запись токенов доступа к BX24 в файл """
#     with open(path_secret_file, 'w') as secrets_file:
#         json.dump(data, secrets_file)


def save_secrets(data):
    """ Запись токенов доступа к BX24 в файл """
    with open(path_secret_file, 'r') as secrets_file:
        data_old = json.load(secrets_file)
        data["client_secret"] = data_old["client_secret"]
        data["client_id"] = data_old["client_id"]

    with open(path_secret_file, 'w') as secrets_file:
        json.dump(data, secrets_file)


def update_secrets(auth_token, expires_in, refresh_token):
    """ Обновление токенов доступа к BX24 в файле """
    with open(path_secret_file) as secrets_file:
        data = json.load(secrets_file)

    data["auth_token"] = auth_token
    data["expires_in"] = expires_in
    data["refresh_token"] = refresh_token

    with open(path_secret_file, 'w') as secrets_file:
        json.dump(data, secrets_file)


def get_secret(key):
    """ Получение секрета BX24 по ключу """
    with open(path_secret_file) as secrets_file:
        data = json.load(secrets_file)

    return data.get(key)


def get_secrets_all():
    """ Получение секрета BX24 """
    with open(path_secret_file) as secrets_file:
        data = json.load(secrets_file)

    return data
