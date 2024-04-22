from rest_framework import serializers
from .models import NewUser

# class UserSerializer(serializers.ModelSerializer):
#     invited_users_count = serializers.SerializerMethodField()
#
#     class Meta:
#         model = NewUser
#         fields = ['id', 'phone_number', 'activated_invite_code', 'invite_code', 'invited_users_count']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewUser
        fields = ['id', 'phone_number', 'invite_code',
                    'activated_invite_code', 'invited_users']
    def get_invited_users_count(self, obj):
        return obj.invited_users.count()

class AuthCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

class VerifyAuthCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    auth_code = serializers.CharField(max_length=4)

class ActivateInviteCodeSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=10)

class InvitedUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewUser
        fields = ['id', 'username', 'phone_number']