from django.urls import path, include
from accounts.views import RegisterPage, CustomLoginView, CustomLogoutView, ProfileView

app_name = "accounts"

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("register/", RegisterPage.as_view(), name="register"),
    path("logout/", CustomLogoutView.as_view(next_page="/"), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("", include("django.contrib.auth.urls")),
]
