import re

from django import forms

from .models import User


class PhoneSmsForm(forms.Form):
    """Форма проверки номера телефона."""

    phone_number = forms.CharField(max_length=12)
    confirmation_code = forms.CharField(required=False)


    def clean_phone_number(self):
        """Метод валидации номера телефона."""
        cleaned_data = self.cleaned_data['phone_number']
        pattern = r'\+7\d{10}$'
        if not re.match(pattern, cleaned_data):
            raise forms.ValidationError(
                "Номер телефона должен начинаться с +7 и иметь 11 цифр"
            )
        return cleaned_data

class ProfileForm(forms.ModelForm):
    """Форма профиля пользователя."""

    class Meta:
        model = User
        fields = ('phone_number', 'inviter_code',)


class ProfileUpdateForm(forms.ModelForm):
    """Форма обновления профиля пользователя."""

    def clean_inviter_code(self):
        """Метод валидации реферального кода пригласителя."""
        cleaned_data = self.cleaned_data['inviter_code']

        if cleaned_data != self.instance.inviter_code:
            if cleaned_data is not None:
                if not User.objects.filter(my_invite_code=cleaned_data).exists():
                    raise forms.ValidationError('Введенный вами код не существует')
                elif cleaned_data == self.instance.my_invite_code:
                    raise forms.ValidationError('Вы не можете использовать собственный реферальный код')
                elif User.objects.filter(my_invite_code=cleaned_data).exists():
                    if self.instance.my_invite_code == User.objects.get(
                            my_invite_code=cleaned_data).inviter_code:
                        raise forms.ValidationError(
                            'Вы не можете использовать код пользователя, которого пригласили сами'
                        )
        else:
            cleaned_data = self.instance.inviter_code

        return cleaned_data

    class Meta:
        model = User
        fields = ('inviter_code',)
