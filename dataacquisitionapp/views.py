from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from clientbx24 import tokens


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
        return render(request, 'dataacquisitionapp/install.html')
    else:
        return JsonResponse({'message': 'Method not allowed'}, status=405)


@csrf_exempt
@xframe_options_exempt
def index_api_view(request):
    if request.method == 'POST':
        return render(request, 'dataacquisitionapp/index.html', context={})
    else:
        return JsonResponse({'message': 'Method not allowed'}, status=405)


# from rest_framework import views
# from django.shortcuts import render
# from django.views.decorators.clickjacking import xframe_options_exempt
#
# from clientbx24 import tokens
#
#
# class InstallApiView(views.APIView):
#     @xframe_options_exempt
#     def post(self, request):
#         data = {
#             "domain": request.query_params.get("DOMAIN", ""),
#             "auth_token": request.data.get("AUTH_ID", ""),
#             "expires_in": request.data.get("AUTH_EXPIRES", 3600),
#             "refresh_token": request.data.get("REFRESH_ID", ""),
#             "application_token": request.query_params.get("APP_SID", ""),
#             'client_endpoint': f'https://{request.query_params.get("DOMAIN", "")}/rest/',
#         }
#         tokens.save_secrets(data)
#         return render(request, 'dataacquisitionapp/install.html')
#
#
# class IndexApiView(views.APIView):
#     @xframe_options_exempt
#     def post(self, request):
#         return render(request, 'dataacquisitionapp/index.html', context={})
