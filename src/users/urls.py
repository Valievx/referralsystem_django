from django.urls import path, include

from users.views import (SmsCodeCreateView, SmsCodeVerifyView,
                         ProfileDetailView, ProfileUpdateView)


app_name = 'users'


urlpatterns = [
    path('signup/', SmsCodeCreateView.as_view(), name='web_signup'),
    path('token/', SmsCodeVerifyView.as_view(), name='web_token'),
    path('profile/', ProfileDetailView.as_view(), name='web_profile'),
    path('profile/update', ProfileUpdateView.as_view(), name='web_profile_update'),
]
