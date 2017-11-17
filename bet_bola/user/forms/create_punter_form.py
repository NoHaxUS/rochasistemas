from django import forms
from django.forms import extras
from user.models import Punter


class CreatePunterForm(forms.ModelForm):	
	
	class Meta:
		model = Punter
		fields = ['first_name','last_name','username','password','email','date_joined','mobile_phone']
		
