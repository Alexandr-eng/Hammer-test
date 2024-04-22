from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import NewUser, generate_auth_code
from .serializers import UserSerializer, AuthCodeSerializer, \
    VerifyAuthCodeSerializer, ActivateInviteCodeSerializer, \
    InvitedUsersSerializer
import time
import random
from django.shortcuts import render


def user_interface(request):
    return render(request, 'us_interface.html')


class UserViewSet(viewsets.ModelViewSet):
    queryset = NewUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def profile(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def activate_invite_code(self, request):
        serializer = ActivateInviteCodeSerializer(data=request.data)
        if serializer.is_valid():
            invite_code = serializer.validated_data['invite_code']
            try:
                invited_user = NewUser.objects.get(invite_code=invite_code)
                user = request.user
                user.activated_invite_code = invite_code
                user.invited_users.add(invited_user)
                user.save()
                return Response({'detail': 'Инвайт-код активирован'},
                            status=status.HTTP_200_OK)
            except NewUser.DoesNotExist:
                return Response({'detail': 'Инвайт-код не найден'},
                            status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def invited_users(self, request):
        user = request.user
        invited_users = user.invited_users.all()
        serializer = InvitedUsersSerializer(invited_users, many=True)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def request_auth_code(request):
    serializer = AuthCodeSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        # Генерируем четырехзначный код
        auth_code = '{:04d}'.format(random.randint(0, 9999))
        try:
            # Пытаемся получить пользователя по номеру телефона
            user = NewUser.objects.get(phone_number=phone_number)
        except NewUser.DoesNotExist:
            # Если пользователь не найден, создаем нового пользователя
            user = NewUser.objects.create(phone_number=phone_number)
        # Обновляем код аутентификации и сохраняем пользователя
        user.auth_code = auth_code
        user.save()
        # Возвращаем четырехзначный код вместо токена
        return Response({'auth_code': auth_code}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_auth_code(request):
    serializer = VerifyAuthCodeSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        auth_code = serializer.validated_data['auth_code']
        try:
            user = NewUser.objects.get(phone_number=phone_number,
                                       auth_code=auth_code)
            user.auth_code = ''
            user.save()
            # Вместо токена возвращаем четырехзначный код
            return Response({'auth_code': auth_code},
                            status=status.HTTP_200_OK)
        except NewUser.DoesNotExist:
            return Response({'detail': 'Неверный код авторизации'},
                            status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
