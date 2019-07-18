# from rest_framework.views import APIView
# from django.core.mail import send_mail
# from user.models import CustomUser
# import json

# class ForgotPassword(APIView):
#     def post(self, request):
#         data = json.loads(request.data.get('data'))
#         CustomUser.objects.filter(email=data.get('email'))
#         send_mail()