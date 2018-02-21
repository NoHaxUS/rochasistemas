from django.http import JsonResponse

class UnicodeJsonResponse(JsonResponse):
    def __init__(self, data={}, **kwargs):
        super().__init__(data, json_dumps_params={'ensure_ascii':False}, **kwargs)