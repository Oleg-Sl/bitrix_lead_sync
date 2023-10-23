import requests
from urllib.parse import urlparse, parse_qs
import base64
from time import sleep
from clientbx24.requests import Bitrix24
from clientbx24 import tokens
import logging
import traceback
import pprint


class MyHandler:
    def __init__(self):
        self.bx24 = Bitrix24()
        self.logger = logging.getLogger("CreatorProduct")
        self.logger.setLevel(logging.INFO)
        handler = logging.handlers.TimedRotatingFileHandler("logs/error_create_poduct.log", when="midnight", interval=1, backupCount=10)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    @staticmethod
    def find_rate_by_value(rate_list, value):
        for item in rate_list:
            if float(item['RATE']) == value:
                return item['ID']
        return None

    @staticmethod
    def find_measure_by_code(measure_list, value):
        for item in measure_list:
            if item['code'] == value:
                return item['id']
        return None

    @staticmethod
    def download_file(file_url):
        domain = tokens.get_secret("domain")
        url = f"https://{domain}{file_url}"
        response = requests.get(url)
        if response.status_code == 200:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            filename = query_params.get('fieldName', [''])[0]
            file_base64 = base64.b64encode(response.content).decode()
            return [f"{filename}.png", file_base64]

    def get_data_files(self, files_info):
        files_data = []
        for file_info in files_info:
            file_url = file_info.get("value", {}).get("downloadUrl", {})
            f_data = self.download_file(file_url)
            if f_data:
                files_data.append(f_data)
        return files_data

    def handle(self, lead_id, product_item_id, catalog_id):
        try:
            response = self.bx24.call("batch", {
                "halt": 0,
                "cmd": {
                    "product_item": f"crm.item.productrow.get?id={product_item_id}",
                    "vat_list": "crm.vat.list",
                    "measure_list": "catalog.measure.list"
                }
            })
            response_result = response.get("result", {}).get("result", {})
            response_error = response.get("result", {}).get("result_error", {})
            if not response_result or response_error or not isinstance(response_result, dict):
                self.logger.info({
                    "methods": f"crm.item.productrow.get?id={product_item_id}, crm.vat.list, catalog.measure.list",
                    "response": response
                })
                return

            product_item = response_result.get("product_item", {}).get("productRow", {})
            vat_list = response_result.get("vat_list", {})
            measure_list = response_result.get("measure_list", {}).get("measures", [])

            product_id = product_item.get("productId")

            pprint.pprint(product_item)

            response = self.bx24.call("batch", {
                "halt": 0,
                "cmd": {
                    "product": f"crm.product.get?id={product_id}",
                    "variation": f"catalog.product.get?id={product_id}",
                    "product_2": "crm.product.get?id=$result[variation][product][parentId][value]"
                }
            })
            response_result = response.get("result", {}).get("result", {})
            response_error = response.get("result", {}).get("result_error", {})
            if not response_result or not isinstance(response_result, dict):
                self.logger.info({
                    "methods": f"crm.product.get?id={product_id}, catalog.product.get?id={product_id}, crm.product.get?id=$result[variation][product][parentId][value]",
                    "response": response
                })
                return

            product = response_result.get("product", {}) if response_result.get("product", {}) else response_result.get("product_2", {})

            product_new_name = product_item.get('productName')
            product_new_price = product_item.get('priceExclusive')
            product_item_price = product_item.get('price')
            product_quantity = product_item.get('quantity')
            product_measure_code = product_item.get('measureCode')
            product_measure_id = self.find_measure_by_code(measure_list, product_measure_code)
            product_new_vat_include = product_item.get('taxIncluded')
            product_new_vat_val = product_item.get('taxRate')
            product_new_vat_id = self.find_rate_by_value(vat_list, product_new_vat_val)

            self.logger.info(product)
            # picture_list = product.get("PROPERTY_101") if product.get("PROPERTY_101") else product.get("PREVIEW_PICTURE")
            picture_url = None
            if product.get("PROPERTY_101"):
                picture_url = product.get("PROPERTY_101", [{}])[0].get("value", {}).get("downloadUrl", {})
            if product.get("PREVIEW_PICTURE", {}) and product.get("PREVIEW_PICTURE", {}).get("downloadUrl"):
                picture_url = product.get("PREVIEW_PICTURE", {}).get("downloadUrl")

            sleep(1)
            result_products_add = self.bx24.call("crm.product.add", {
                "fields": {
                    'CURRENCY_ID': 'RUB',
                    'NAME': product_new_name,
                    'PREVIEW_PICTURE': {"fileData": self.download_file(picture_url)},
                    'PRICE': product_new_price if product_new_vat_include == 'N' else product_item_price,
                    'VAT_ID': product_new_vat_id,
                    'VAT_INCLUDED': product_new_vat_include,
                    'MEASURE': product_measure_id,
                    'ACTIVE': 'N',
                    'SECTION_ID': catalog_id
                }
            })

            product_new_id = result_products_add.get("result")
            if not product_new_id:
                self.logger.info({
                    "method": f"crm.product.add",
                    "params": {
                        'CURRENCY_ID': 'RUB',
                        'NAME': product_new_name,
                        'PREVIEW_PICTURE': {"fileData": self.download_file(picture_url)} if picture_url else [],
                        'PRICE': product_new_price,
                        'VAT_ID': product_new_vat_id,
                        'VAT_INCLUDED': product_new_vat_include,
                        'MEASURE': product_measure_id,
                    },
                    "response": result_products_add
                })

                return

            sleep(1)

            result_add = self.bx24.call("crm.item.productrow.add", {
                "fields": {
                    "productId": product_new_id,
                    "ownerType": "L",
                    "ownerId": lead_id,
                    "price": product_item_price,
                    "quantity": product_quantity,
                    "taxRate": product_new_vat_val,
                    "taxIncluded": product_new_vat_include,
                }
            })

            if not result_add.get("result", {}).get("productRow", {}):
                self.logger.info({
                    "method": f"crm.product.add",
                    "params": {
                        'CURRENCY_ID': 'RUB',
                        'NAME': product_new_name,
                        'PREVIEW_PICTURE': {"fileData": self.download_file(picture_url)},
                        'PRICE': product_new_price,
                        'VAT_ID': product_new_vat_id,
                        'VAT_INCLUDED': product_new_vat_include,
                        'MEASURE': product_measure_id,
                    },
                    "response": result_products_add
                })

                return

            sleep(1)

            result_products = self.bx24.call("crm.item.productrow.delete", {"id": product_item_id})

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            self.logger.error(traceback.format_exc())
