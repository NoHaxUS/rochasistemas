from django.conf import settings
from rest_framework import status
from utils.response import UnicodeJsonResponse

class ReadKeyMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        
        if 'admin' in request.path:
            return self.get_response(request)

        if not settings.DEV_MODE and not request.headers.get('SecurityAuthorization') == 'aW6dvtS4XvfYXutA':
                return UnicodeJsonResponse({'status': 'failed'}, status=status.HTTP_403_FORBIDDEN)
        
        return self.get_response(request)