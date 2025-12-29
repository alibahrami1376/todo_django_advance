from django.shortcuts import render
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from accounts.forms import RegisterForm
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from todo.models import Task

# Create your views here.
class RegisterPage(FormView):

    template_name = "register.html"
    form_class = RegisterForm
    success_url = "/"
    # redirect_authenticated_user = True
    def form_valid(self, form):
        user = form.save()
        # if user is not None:
        #     login(self.request, user)
        return super().form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("/")
        return super().get(*args, **kwargs) 
         
class CustomLoginView(LoginView):
    template_name = "login.html"
    redirect_authenticated_user = True
    def get_success_url(self):
        return "/"

class CustomLogoutView(LogoutView):
    next_page = "/"
    
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "profile.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's profile
        try:
            profile = user.profile
        except profile.DoesNotExist:
            profile = None
        
        # Get task statistics
        if profile:
            tasks = Task.objects.filter(user=profile)
            total_tasks = tasks.count()
            completed_tasks = tasks.filter(complete=True).count()
            pending_tasks = tasks.filter(complete=False).count()
        else:
            total_tasks = 0
            completed_tasks = 0
            pending_tasks = 0
        
        context.update({
            'profile': profile,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
        })
        
        return context
