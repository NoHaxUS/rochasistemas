
class RewardSerializer(serializers.HyperlinkedModelSerializer):
	who_rewarded_the_winner = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')
	real_value = serializers.SerializerMethodField()

	class Meta:
		model = Reward
		fields = ('who_rewarded_the_winner','date','real_value')

	def get_real_value(self, reward):
		return reward.real_value

