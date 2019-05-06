from rest_framework import serializers
from core.models import Store
from user.models import Admin


class AdminSerializer(serializers.HyperlinkedModelSerializer):	
		
	password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
	my_store = serializers.SlugRelatedField(read_only=True, slug_field='id')	

	def create(self, validated_data):				
		obj = Admin(**validated_data)		
		print(self.context['request'].GET.get('store'))
		store = Store.objects.get(id=self.context['request'].GET.get('store'))
		obj.my_store=store
		obj.save()
		return obj

	class Meta:
		model = Admin
		fields = ('id','username','password','first_name','email','my_store')
