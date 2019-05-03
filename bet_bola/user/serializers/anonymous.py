
class AnonymousUserSerializer(serializers.HyperlinkedModelSerializer):		

	class Meta:
		model=NormalUser
		fields = ('id','first_name','cellphone')

	def create(self, validated_data):				
		obj = NormalUser(**validated_data)		
		store = Store.objects.get(id=self.context['request'].GET.get('store'))
		obj.my_store=store
		obj.save()
		return obj