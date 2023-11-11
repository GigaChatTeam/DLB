from django.http import HttpResponse

from ..views.exceptions import AccessDenied


class AccessDeniedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    @staticmethod
    def process_exception(_, exception):
        if not isinstance(exception, AccessDenied):
            return None
        return HttpResponse(status=403)
