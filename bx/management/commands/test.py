from django.core.management.base import BaseCommand
from django.conf import settings
from time import sleep
import logging
import pprint


from clientbx24.requests import Bitrix24
# from bx.tasks.test import


class Command(BaseCommand):
    # method = 'crm.lead.get'
    help = 'Test'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bx24 = Bitrix24()
        # self.logger = logging.getLogger("CommandEventLeads")
        # self.logger.setLevel(logging.INFO)
        # handler = logging.handlers.TimedRotatingFileHandler("logs/offline_events/lead.log", when="midnight", interval=1, backupCount=10)
        # formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        # handler.setFormatter(formatter)
        # self.logger.addHandler(handler)

    def handle(self, *args, **kwargs):
        lead_id = 273
        product_item_id = 433

        result_item_products = self.bx24.call("crm.item.productrow.get", {"id": product_item_id})
        product_item = result_item_products.get("result", {}).get("productRow", {})
        print(result_item_products)
        sleep(1)

        product_id = product_item.get("productId")
        print(product_id)
        result_products = self.bx24.call("crm.product.get", {"id": product_id})
        product = result_products.get("result", {})
        print(product)
        sleep(1)

        result_products_add = self.bx24.call("crm.product.add", {"fields": product})
        product_new_id = result_products_add.get("result")
        if not product_new_id:
            return

        print(result_products_add)
        sleep(1)
        result_add = self.bx24.call("crm.item.productrow.add", {
            "fields": {
                "productId": product_new_id,
                "ownerType": "L",
                "ownerId": lead_id,
                "price": product_item.get("price"),
                "quantity": product_item.get("quantity"),
                "taxRate": product_item.get("taxRate"),
                "taxIncluded": product_item.get("taxIncluded"),
            }
        })

        print(result_add)
        if not result_add.get("result", {}).get("productRow", {}):
            return


        #
        # sleep(1)
        # print(product_item_id)
        # result_products = self.bx24.call("crm.item.productrow.delete", {"id": product_item_id})
        #
        # print(result_products)
        # result_products = self.bx24.call("batch", {
        #     "1": "crm.item.productrow.get", {"id": product_item_id})
        # })



# ?crm.item.productrow.get
