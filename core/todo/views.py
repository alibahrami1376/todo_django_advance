from django.shortcuts import redirect
from django.views.generic.list import ListView
from django.views.generic.edit import (
    CreateView,
    UpdateView,
    DeleteView,    
)
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .models import Task
from todo.forms import TaskUpdateForm
from django.http import HttpResponse 

class TaskCreateView(LoginRequiredMixin, CreateView):
    """
    View to create a new task,
    automatically linking it to the logged-in user's profile
    """
    model = Task
    fields = ['title', 'description']  
    template_name = 'todo/todo_create.html'
    success_url = reverse_lazy('todo:task_list')

    def form_valid(self, form):
        form.instance.user = self.request.user.profile 
        return super(TaskCreateView, self).form_valid(form)

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    """
    View to delete a task,
    restricted to tasks of the logged-in user's profile
    GET requests are treated as POST to allow direct deletion
    """
    model = Task
    context_object_name = "task"
    success_url = reverse_lazy("todo:task_list")

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user.profile)

class TaskUpdateView(LoginRequiredMixin,UpdateView):
    """
    View to update a task,
    restricted to the logged-in user's tasks
    """
    model = Task
    success_url = reverse_lazy("todo:task_list")
    form_class = TaskUpdateForm
    template_name = "todo/todo_edit.html"

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user.profile)

class TaskToggleView(LoginRequiredMixin,View):
    """
    View to toggle the completion status of a task
    """
    def post(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task,pk=pk,user=self.request.user.profile)
        task.complete = not task.complete
        task.save()
        return redirect("todo:task_list")

class TaskDetailView(LoginRequiredMixin,DetailView):
    """
    View to show task details for the logged-in user
    """
    model = Task
    template_name = "todo/todo_detail.html"
    context_object_name = "todo"

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user.profile)
    
class TaskListView(LoginRequiredMixin,ListView):
    """
    # View to list all tasks of the logged-in user
    """
    model = Task
    context_object_name = "tasks"
    template_name = "todo/todo_list.html"

    def get_queryset(self):
       return Task.objects.filter(user=self.request.user.profile)

