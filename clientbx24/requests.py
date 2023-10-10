#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Wrapper over Bitrix24 cloud API"""
import json
import time
import logging
from requests import adapters, post, exceptions

from . import tokens

adapters.DEFAULT_RETRIES = 10


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Bitrix24(metaclass=SingletonMeta):
    API_URL = 'https://%s/rest/%s.json'
    OAUTH_URL = 'https://oauth.bitrix.info/oauth/token/'
    TIMEOUT = 60

    def __init__(self):
        token_data = tokens.get_secrets_all()
        self.domain = token_data.get("domain", None)
        self.auth_token = token_data.get("auth_token", None)
        self.refresh_token = token_data.get("refresh_token", None)
        self.client_id = tokens.get_secret("client_id")
        self.client_secret = tokens.get_secret("client_secret")
        self.logger = logging.getLogger("Bitrix24")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler("offline_events.log")
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _refresh_tokens(self):
        try:
            response = post(
                self.OAUTH_URL,
                params={'grant_type': 'refresh_token', 'client_id': self.client_id, 'client_secret': self.client_secret,
                        'refresh_token': self.refresh_token}
            )
            result = json.loads(response.text)

            if 'access_token' in result and 'refresh_token' in result and 'expires_in' in result:
                self.auth_token = result['access_token']
                self.refresh_token = result['refresh_token']
                self.expires_in = result['expires_in']
                tokens.update_secrets(self.auth_token, self.expires_in, self.refresh_token)
                return True
        except Exception as e:
            self.logger.error(f"Error refreshing tokens: {e}")
        return False

    def call(self, method, params):
        try:
            url = self.API_URL % (self.domain, method)
            url += '?auth=' + self.auth_token
            headers = {
                'Content-Type': 'application/json',
            }
            response = post(url, data=json.dumps(params), headers=headers, timeout=self.TIMEOUT)
            result = json.loads(response.text)
        except (ValueError, KeyError) as e:
            self.logger.error(f"Error decoding API response: {e}")
            result = {'error': f'Error on decode api response [{response.text}]'}
        except exceptions.ReadTimeout as e:
            self.logger.error(f"Timeout waiting expired [{str(self.TIMEOUT)} sec]: {e}")
            result = {'error': f'Timeout waiting expired [{str(self.TIMEOUT)} sec]'}
        except exceptions.ConnectionError as e:
            self.logger.error(f"Max retries exceeded [{adapters.DEFAULT_RETRIES}]: {e}")
            result = {'error': f'Max retries exceeded [{adapters.DEFAULT_RETRIES}]'}

        if 'error' in result and result['error'] in ('NO_AUTH_FOUND', 'expired_token'):
            if self._refresh_tokens():
                return self.call(method, params)
        elif 'error' in result and result['error'] == 'QUERY_LIMIT_EXCEEDED':
            time.sleep(2)
            return self.call(method, params)

        return result

    def batch(self, params):
        if 'halt' not in params or 'cmd' not in params:
            return {'error': 'Invalid batch structure'}

        return self.call("batch", params)
