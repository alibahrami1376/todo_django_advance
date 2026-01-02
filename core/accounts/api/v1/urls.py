from django.urls import path, include
from accounts.api.v1.views import RegistrationApiView


urlpatterns = [
    path("registration/",RegistrationApiView.as_view(),name="registration",),
]
