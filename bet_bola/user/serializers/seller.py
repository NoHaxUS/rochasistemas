from rest_framework import serializers
from user.models import Manager, Seller, Punter
from core.models import Store
from utils.models import SellerComission
from ticket.models import Ticket
from django.db.models import Q

class SellerSerializer(serializers.HyperlinkedModelSerializer):

    my_manager = serializers.SlugRelatedField(queryset=Manager.objects.all(), allow_null=True, required=False, slug_field='username', error_messages={"does_not_exist": "{value} não existe."})
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True, allow_null=True, error_messages={"does_not_exist": "{value} não existe. PÇPÇ"})
    
    def create(self, validated_data):
        user = self.context['request'].user
        store = user.my_store
        obj = Seller(**validated_data)
        obj.my_store=store
        if user.user_type == 3:
            obj.my_manager = user.manager
        obj.save()

        SellerComission.objects.create(
            seller_related=obj,
            store=store
        )

        return obj

    def reset_ticket_from_current_manager(self, current):
        tickets = Ticket.objects.filter(Q(payment__status=2, payment__who_paid__seller__my_manager__pk=current.pk, store=current.my_store) & 
            (Q(closed_in_for_manager=False) | Q(closed_out_for_manager=False, status__in=[4,2]))).distinct().exclude(Q(status__in=[5,6]) | Q(available=False)).order_by('-creation_date')
        tickets.update(closed_in_for_manager=True, closed_out_for_manager=True)
        
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        password = validated_data.get('password', instance.password)
        if password:
            instance.password = password
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.cellphone = validated_data.get('cellphone', instance.cellphone)
        instance.address = validated_data.get('address', instance.address)
        instance.cpf = validated_data.get('cpf', instance.cpf)
        
        if validated_data.get('my_manager') and instance.my_manager:
            self.reset_ticket_from_current_manager(instance.my_manager)

        instance.my_manager = validated_data.get('my_manager', instance.my_manager)
        instance.email = validated_data.get('email', instance.email)
        instance.can_cancel_ticket = validated_data.get('can_cancel_ticket', instance.can_cancel_ticket)
        instance.limit_time_to_cancel = validated_data.get('limit_time_to_cancel', instance.limit_time_to_cancel)
        instance.can_sell_unlimited = validated_data.get('can_sell_unlimited', instance.can_sell_unlimited)

        instance.save()
        return instance

    def validate_email(self, value):
        if self.context['request'].method == 'POST' and value:
            if Seller.objects.filter(email=value):
                raise serializers.ValidationError("Email já cadastrado.")
            return value
        return value
    
    def validate_limit_time_to_cancel(self, value):
        user = self.context['request'].user		
        if user.user_type == 3:
            if self.instance and not user.manager.can_change_limit_time and not self.instance.limit_time_to_cancel == value:
                raise serializers.ValidationError("Usuário não tem permissão para alterar o tempo limite de cancelamento.")
        return value
    
    def validate_username(self, value):
        user = self.context['request'].user				
        if user.user_type == 3:			
            if self.instance and not self.instance.username == value:
                raise serializers.ValidationError("Usuário não tem permissão para alterar o username.")
        return value

    class Meta:
        model=Seller
        fields = ('id','username','first_name','password','cellphone','address','cpf','can_sell_unlimited','credit_limit','limit_time_to_cancel','my_manager','email','can_cancel_ticket','is_active')
