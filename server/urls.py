from django.http import HttpResponse
from django.urls import path, include

from .views import handlers


def passer(_):
    return HttpResponse(status=501)


urlpatterns = [
    path('history/', include([
        path('channels', handlers.UsersLoader.channels),
        path('channels/<int:channel>/', include([
            path('messages', handlers.UsersLoader.messages),
            path('users', passer),
            path('permissions', passer),
            path('admin/', include([
                path('messages/', include([
                    path('versions', passer),
                    path('deleted', passer)
                ])),
                path('permissions', passer),
                path('stats', passer)
            ]))
        ]))
    ]))
]
