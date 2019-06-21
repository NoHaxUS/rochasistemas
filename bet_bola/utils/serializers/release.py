from rest_framework import serializers
from user.models import CustomUser as User
from utils.models import Release


class ReleaseSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.SlugRelatedField(queryset = User.objects.filter(user_type__in=[2,3]), slug_field='pk')    
    creation_date = serializers.DateTimeField(format='%d %B %Y', read_only=True)

    def to_representation(self, obj):           
        return {
                "id": obj.pk,
                "user": obj.user.username,
                "value": obj.value,
                "creation_date": obj.creation_date.strftime('%d %B %Y'),
                "description": obj.description 
            }        

    class Meta:
        model = Release
        fields = ("id",'user', 'value', 'creation_date', 'description')