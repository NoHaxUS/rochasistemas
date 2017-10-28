from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Generic_User(User):
	mobile_phone = models.CharField(max_length=25)
	birthday = models.DateTimeField(null=True)
	
	class Meta:
		abstract=True

class Seller(Generic_User):
	cpf = models.CharField(max_length=10)
	address = models.CharField(max_length=75)

class Punter(Generic_User):
	pass