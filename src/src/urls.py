from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import SimpleRouter

from users.views import (create_token, create_user,
                         UserView, UserProfileGetPath)


router = SimpleRouter()
router.register('users', UserView, basename='user')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='main/index.html')),
    path('api/auth/signup/', create_user, name='signup'),
    path('api/auth/token/', create_token, name='token'),
    path('api/profile/', UserProfileGetPath.as_view(), name='profile'),
    path('api/', include(router.urls), ),
    path('user/', include('users.urls', namespace='user')),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
]
