from django.urls import include, path
# from rest_framework import routers

from . import views
# from .views import (
#     IndexApiView,
#     InstallApiView
# )

app_name = 'eventsapp'
# router = routers.DefaultRouter()


urlpatterns = [
    path('install/', views.install_api_view, name='install'),
    path('index/', views.index_api_view, name='index'),

    # path('index/', IndexApiView.as_view()),
    # path('install/', InstallApiView.as_view()),
]
