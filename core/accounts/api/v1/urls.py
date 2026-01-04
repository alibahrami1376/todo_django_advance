from django.urls import path
from accounts.api.v1.views import (
    RegistrationApiView,
    CustomAuthToken,
    CustomDiscardAuthToken,
    ChangePasswordApiView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [

    #registration
    path("registration/",RegistrationApiView.as_view(),name="registration"),
    path("change-password/",ChangePasswordApiView.as_view(),name="change-password"),
    #token
    path("token/login/",CustomAuthToken.as_view(),name="token-login"),
    path("token/logout/",CustomDiscardAuthToken.as_view(),name="token-logout"),
    #jwt
    path('jwt/create', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('jwt/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
