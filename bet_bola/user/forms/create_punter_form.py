from django.contrib.auth.forms import UserCreationForm
from django.forms import extras
from user.models import Punter


class CreatePunterForm(UserCreationForm):	
	def __init__(self, *args, **kwargs):		
		super(CreatePunterForm, self).__init__(*args, **kwargs)					
		self.fields['mobile_phone'].label = 'Telefone'
	
	class Meta:
		model = Punter
		fields = ['first_name','last_name','username','password1','password2','email','mobile_phone']
		
