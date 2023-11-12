from django.http import JsonResponse

from ..views.exceptions import MissingValues


class MissingParametersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    @staticmethod
    def process_exception(_, exception):
        if not isinstance(exception, MissingValues):
            return None
        return JsonResponse({
            'status': 'Refused',
            'reason': 'IncorrectArguments',
            'arguments': {
                'invalid': exception.invalid,
                'missing': exception.missing
            }
        }, status=406)
