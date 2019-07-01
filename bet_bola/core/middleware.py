from django.conf import settings
from rest_framework import status
from utils.response import UnicodeJsonResponse

class ReadKeyMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        
        if not request.headers.get('Proxy-Authorization') == 'aW6dvtS4XvfYXutA':
            if not settings.DEV_MODE:
                return UnicodeJsonResponse(status=status.HTTP_403_FORBIDDEN)
        response = self.get_response(request)
        return response