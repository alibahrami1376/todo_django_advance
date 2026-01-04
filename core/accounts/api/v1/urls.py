from django.urls import path
from accounts.api.v1.views import (
    RegistrationApiView,
    CustomAuthToken,
    CustomDiscardAuthToken,
    ChangePasswordApiView,
    ProfileApiView,
    TestEmailSend,
    ActivationResendApiView,
    ActivationApiView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [

    #registration
    path("registration/",RegistrationApiView.as_view(),name="registration"),
    #change-password
    path("change-password/",ChangePasswordApiView.as_view(),name="change-password"),
    # activation
    path("activation/confirm/<str:token>",ActivationApiView.as_view(),name="activation"),
    # resend activation
    path("activation/resend/",ActivationResendApiView.as_view(),name="activation-resend"),
    #profile
    path("profile/",ProfileApiView.as_view(), name="profile"),
    #emial
    path("test-email",TestEmailSend.as_view(), name="test-email"),
    #token
    path("token/login/",CustomAuthToken.as_view(),name="token-login"),
    path("token/logout/",CustomDiscardAuthToken.as_view(),name="token-logout"),
    #jwt
    path('jwt/create', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('jwt/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
