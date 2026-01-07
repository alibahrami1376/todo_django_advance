from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from accounts.forms import RegisterForm
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login

from todo.models import Task


class RegisterPage(FormView):
    """
    User registration view with auto-login after successful signup
    """

    template_name = "register.html"
    form_class = RegisterForm
    success_url = "/"

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("/")
        return super().get(*args, **kwargs)


class CustomLoginView(LoginView):
    """
    Custom login view with redirect for already authenticated users
    """

    template_name = "login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return "/"


class CustomLogoutView(LogoutView):
    """
    Custom logout view with next_page = home
    """

    next_page = "/"


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    User profile view showing profile info and task statistics
    """

    template_name = "profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = getattr(self.request.user, "profile", None)

        tasks = Task.objects.filter(user=profile) if profile else Task.objects.none()
        context.update(
            {
                "profile": profile,
                "total_tasks": tasks.count(),
                "completed_tasks": tasks.filter(complete=True).count(),
                "pending_tasks": tasks.filter(complete=False).count(),
            }
        )
        return context
