from rest_framework.exceptions import APIException
from rest_framework import status

class NotAllowedException(APIException):
	status_code = status.HTTP_401_UNAUTHORIZED
	default_detail = 'Você não pode realizar essa ação.'