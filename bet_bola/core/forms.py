from django import forms
from .models import Cotation,BetTicket,Game,Championship

class BetTicketForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		#self.bets = kwargs.pop('bets')
		super(BetTicketForm, self).__init__(*args, **kwargs)			
		self.fields.__setitem__('cotations',forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=([(cotation.pk, cotation) for cotation in Cotation.objects.all()])))

	def get_form_kwargs(self):
		# pass "user" keyword argument with the current user to your form
		kwargs = super(BetTicketForm, self).get_form_kwargs()
		print(kwargs)
		kwargs['user'] = self.request.user
		kwargs['creation_date'] = datetime.now()
		return kwargs

	class Meta:
		model = BetTicket
		fields = '__all__'
		exclude = ['punter','seller','creation_date','reward']