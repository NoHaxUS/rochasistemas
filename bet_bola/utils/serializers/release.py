from rest_framework import serializers
from user.models import CustomUser as User
from utils.models import Release


class ReleaseSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.SlugRelatedField(queryset = User.objects.filter(user_type__in=[2,3]), slug_field='username')    
    creation_date = serializers.DateTimeField(format='%d/%m/%Y', read_only=True)

    class Meta:
        model = Release
        fields = ('user', 'value', 'creation_date', 'description')