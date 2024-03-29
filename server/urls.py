from django.http import HttpResponse
from django.urls import path, include

from .views import handlers


def passer(*_, **__):
    return HttpResponse(status=501)


urlpatterns = [
    path('channel/', include([
        path('by/', include([
            path('invitation', handlers.Channels.Invitations.verify_uri),
            path('id/<int:channel>', include([
                path('', passer),
                path('/message', include([
                    path('', passer),
                    path('/<int:message>', passer)
                ])),
                path('/messages/', include([
                    path('history', handlers.Channels.Messages.History.messages),
                    path('edited', passer),
                    path('deleted', passer)
                ])),
            ])),
        ])),
        path('search', passer)
    ])),
    path('user/', include([
        path('@me', passer),
        path('@<int:account>', passer)
    ]))
]
