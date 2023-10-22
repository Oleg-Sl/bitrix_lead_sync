from django.urls import include, path
# from rest_framework import routers

from . import views


app_name = 'eventsapp'
# router = routers.DefaultRouter()


urlpatterns = [
    path('install/', views.install_api_view, name='install'),
    path('index/', views.index_api_view, name='index'),

    path('product-recreation/', views.product_recreation_view),

    # path('index/', IndexApiView.as_view()),
    # path('install/', InstallApiView.as_view()),
]
