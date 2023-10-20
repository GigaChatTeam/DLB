from django.http import HttpResponse
from django.urls import path, include

from .views import handlers


def passer(request):
    return HttpResponse(status=501)


urlpatterns = [
    path('history/', include([
        path('channels', passer),
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
