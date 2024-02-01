from django.http import HttpResponse

from ..views.exceptions import NotFound, AccessDenied


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


class NotFoundMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    @staticmethod
    def process_exception(_, exception):
        if not isinstance(exception, NotFound):
            return None
        return HttpResponse(status=404)