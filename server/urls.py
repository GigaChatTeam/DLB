from django.urls import path
from . import views

urlpatterns = [
    path('history/channels', views.Channels.point),
    path('history/channels/<int:channel>', views.Channels.point)
]
