from uuid import uuid4
import time

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.views.generic import FormView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages

from rest_framework import status, viewsets
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAdminUser)

from .models import User
from .forms import PhoneSmsForm, ProfileForm, ProfileUpdateForm
from .serializers import UserCreateSerializer, UserProfileSerializer


def get_confirmation_code():
    """Генерация 4х значного токена."""
    uuid = uuid4()
    code = str(uuid)[:4]
    return code


def send_confirmation_code(phone_number, confirmation_code):
    """Отправка СМС. Иммитация."""
    message = f'Код авторизации: {confirmation_code}'
    print(message)
    time.sleep(2)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def create_user(request):
    """Регистрация пользователя."""
    if request.method == 'POST':
        serializer = UserCreateSerializer(data=request.data)
        phone_number = request.data.get('phone_number')

        if User.objects.filter(phone_number=phone_number):
            user = User.objects.get(phone_number=request.data['phone_number'])
            send_confirmation_code(
                phone_number=user.phone_number,
                confirmation_code=user.confirmation_code
            )
            return Response(
                {'message': 'Пользователь c таким номером уже существует. '
                 'Код подтверждения отправлен повторно .',
                 'confirmation_code':user.confirmation_code
                 },
                status=status.HTTP_200_OK
            )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.get(phone_number=phone_number)
        confirmation_code = get_confirmation_code()
        serializer.save(
            confirmation_code=confirmation_code
        )
        phone_number = request.data.get('phone_number')
        send_confirmation_code(phone_number, confirmation_code)
        return Response(
            {'confirmation_code':confirmation_code},
            status=status.HTTP_200_OK
        )


@api_view(['POST'])
@permission_classes((AllowAny, ))
def create_token(request):
    """Получение токена по коду из СМС."""
    if request.method == 'POST':
        phone_number = request.data.get('phone_number', None)
        confirmation_code = request.data.get('confirmation_code', None)
        if not phone_number:
            return Response(
                {'phone_number': 'Обязательное поле.'},
                status=status.HTTP_400_BAD_REQUEST)
        if not confirmation_code:
            return Response(
                {'confirmation_code': 'Обязательное поле.'},
                status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, phone_number=phone_number)
        if confirmation_code == user.confirmation_code:
            access_token = str(AccessToken.for_user(user))
            return Response(
                {'message': 'Авторизация прошла успешно',
                 'access_token': access_token
                 }
            )
        return Response('Неверный confirmation_code',
                        status=status.HTTP_400_BAD_REQUEST)


class UserProfileGetPath(APIView):
    """Просмотр и редактирование профиля."""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """Получить информацию о профиле."""
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        """Ввод inviter_code."""
        user = request.user
        if user.inviter_code:
            return Response(
                {'inviter_code': 'Вы уже ввели инвайт-код пригласившего '
                 'вас пользователя.'},
                status=status.HTTP_403_FORBIDDEN)
        inviter_code = request.data.get('inviter_code', None)
        serializer = UserProfileSerializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        if inviter_code == user.my_invite_code:
            return Response(
                {'inviter_code': 'Нельзя вводить свой инвайт-код.'},
                status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return self.get(request)


class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (IsAdminUser,)


class SmsCodeCreateView(FormView):
    """Веб-тест для авторизации: отправка смс кода."""

    form_class = PhoneSmsForm
    template_name = 'main/auth_send_sms.html'
    success_url = reverse_lazy('user:web_token')

    def form_valid(self, form):
        """Метод обрабатывает валидную форму для отправки смс кода."""
        phone_number = form.cleaned_data['phone_number']

        user, created = User.objects.get_or_create(phone_number=phone_number)

        if created or not user.confirmation_code:
            confirmation_code = get_confirmation_code()
            user.confirmation_code = confirmation_code
            user.save()
        confirmation_code = user.confirmation_code

        self.request.session['phone_number'] = phone_number
        self.request.session['confirmation_code'] = confirmation_code

        send_confirmation_code(phone_number, confirmation_code)
        return super().form_valid(form)

class SmsCodeVerifyView(FormView):
    """Веб-тест для авторизации: проверка смс кода."""

    form_class = PhoneSmsForm
    template_name = 'main/auth_verify_sms.html'
    success_url = reverse_lazy('user:web_profile')

    def form_valid(self, form):
        """Метод обрабатывает валидную форму для проверки смс кода."""
        phone_number = form.cleaned_data['phone_number']
        confirmation_code = form.cleaned_data['confirmation_code']

        user = User.objects.filter(phone_number=phone_number).first()

        if user:
            if user.confirmation_code == confirmation_code:
                login(self.request, user)
                return super().form_valid(form)

            error_message = "Неверный код подтверждения"
            return render(
                self.request,
                self.template_name,
                {'form': form, 'error_message': error_message}
            )

        error_message = "Пользователь с указанным номером телефона не найден"
        return render(
            self.request,
            self.template_name,
            {'form': form, 'error_message': error_message}
        )

    def get_context_data(self, **kwargs):
        """Добавляет номер телефона и код подтверждения в контекст."""
        context = super().get_context_data(**kwargs)
        context['phone_number'] = self.request.session.get('phone_number', '')
        context['confirmation_code'] = self.request.session.get('confirmation_code', '')
        return context



class ProfileDetailView(DetailView):
    """Веб-тест для просмотра профиля."""

    model = User
    form_class = ProfileForm
    template_name = 'main/profile.html'

    def get_object(self):
        """Метод возвращает экземпляр пользователя."""
        return self.request.user

    def get_context_data(self, **kwargs):
        """Метод получения списка пользователей,
        которые ввели инвайт код пользователя."""
        context = super().get_context_data(**kwargs)
        invites = User.objects.filter(inviter_code=self.request.user.my_invite_code)
        context['invites'] = invites
        return context


class ProfileUpdateView(UpdateView):
    """Веб-тест для изменения профиля."""

    model = User
    form_class = ProfileUpdateForm
    template_name = 'main/profile_update.html'
    success_url = reverse_lazy('user:web_profile')

    def get_object(self):
        """Метод возвращает экземпляр пользователя."""
        return self.request.user

    def form_valid(self, form):
        """Метод обрабатывает валидную форму."""
        user = form.save(commit=False)
        user.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        """Метод обрабатывает невалидную форму."""
        return super().form_invalid(form)
