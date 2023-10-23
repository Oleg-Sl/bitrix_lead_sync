from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from clientbx24 import tokens
from clientbx24.requests import Bitrix24

from bx.services import handler_create_product


@csrf_exempt
@xframe_options_exempt
def install_api_view(request):
    if request.method == 'POST':
        data = {
            "domain": request.GET.get("DOMAIN", ""),
            "auth_token": request.POST.get("AUTH_ID", ""),
            "expires_in": request.POST.get("AUTH_EXPIRES", 3600),
            "refresh_token": request.POST.get("REFRESH_ID", ""),
            "application_token": request.GET.get("APP_SID", ""),
            'client_endpoint': f'https://{request.GET.get("DOMAIN", "")}/rest/',
        }
        tokens.save_secrets(data)
        return render(request, 'bx/install.html')
    else:
        return JsonResponse({'message': 'Method not allowed'}, status=405)


@csrf_exempt
@xframe_options_exempt
def index_api_view(request):
    if request.method == 'POST':
        return render(request, 'bx/index.html', context={})
    else:
        return JsonResponse({'message': 'Method not allowed'}, status=405)


@csrf_exempt
@xframe_options_exempt
def product_recreation_view(request):
    if request.method == 'POST':
        catalog_id = 137

        token_input = request.GET.get("token")
        if token_input != tokens.get_secret("application_token"):
            return JsonResponse({'message': 'Invalid token'}, status=405)

        lead_id = request.GET.get("lead_id")
        product_item_id = request.GET.get("product_item_id")
        if not lead_id or not product_item_id:
            return JsonResponse({'message': 'Empty lead_id or product_item_id'}, status=405)

        my_handler = handler_create_product.MyHandler()
        my_handler.handle(lead_id, product_item_id, catalog_id)

        # bx24 = Bitrix24()
        # # получение данных товарной позиции
        # result_item_products = bx24.call("crm.item.productrow.get", {"id": product_item_id})
        # product_item = result_item_products.get("result", {}).get("productRow", {})
        # product_id = product_item.get("productId")
        # if not product_id:
        #     return JsonResponse({'message': f'Not found product for product_item: {product_item_id}'}, status=405)
        # return
        #
        # # получение данных продукта из каталога
        # result_products = bx24.call("crm.product.get", {"id": product_id})
        # product = result_products.get("result")
        # if not product:
        #     result_variation_products = bx24.call("catalog.product.get", {"id": product_id})
        #     # return JsonResponse({'message': result_variation_products}, status=405)
        #     product_id = result_variation_products.get("result", {}).get("product", {}).get("parentId", {}).get("value", {})
        #     if product_id:
        #         result_products = bx24.call("crm.product.get", {"id": product_id})
        #         product = result_products.get("result")
        #     else:
        #         return JsonResponse({'message': f"Cann't get data product {product_id}"}, status=405)
        #
        # # создание продукта
        # result_products_add = bx24.call("crm.product.add", {"fields": product})
        # product_new_id = result_products_add.get("result")
        # if not product_new_id:
        #     return JsonResponse({'message': 'Error creating product', "error": result_products_add}, status=405)
        #
        # # добавление созданного товара к лиду
        # result_add = bx24.call("crm.item.productrow.add", {
        #     "fields": {
        #         "productId": product_new_id,
        #         "ownerType": "L",
        #         "ownerId": lead_id,
        #         "price": product_item.get("price"),
        #         "quantity": product_item.get("quantity"),
        #         "taxRate": product_item.get("taxRate"),
        #         "taxIncluded": product_item.get("taxIncluded"),
        #     }
        # })
        # if not result_add.get("result", {}).get("productRow", {}):
        #     return JsonResponse({'message': 'Error adding product to lead'}, status=405)
        #
        # # удаление старой товарной позтции из сделкиq
        # result_products = bx24.call("crm.item.productrow.delete", {"id": product_item_id})
        #
        # # print(result_products)
        # return JsonResponse({'message': 'Success'}, status=200)
