from rest_framework import serializers
from django.conf import settings
from myapp.models import *

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'profile_pic', 'name', 'email', 'phone', 'dob', 'address', 'username', 'password']
        extra_kwargs = {
            'password': {'write_only': True}, 
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)  
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)  #
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        # Construct the full URL for profile_pic
        if instance.profile_pic:
            full_url = request.build_absolute_uri(instance.profile_pic.url)
            representation['profile_pic'] = full_url

        return representation
    


class BankSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = BankAccount
        fields = ['account_number', 'account_holder_name', 'bank_name', 'branch_name', 'ifsc_code', 'user_id', 'user_details']

    def get_user_details(self, obj):
        try:
            user = CustomUser.objects.get(id=obj.user_id)

            print(f"Found user: {user}")  # Debugging output
            return {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
            }
        except CustomUser.DoesNotExist:
            print(f"User with id {obj.user_id} does not exist.")  # Debugging output
            return None

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__' 