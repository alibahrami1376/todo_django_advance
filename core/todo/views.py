from django.shortcuts import redirect
from django.views.generic.list import ListView
from django.views.generic.edit import (
    CreateView,
    UpdateView,
    DeleteView,    
)
from django.views.generic import DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .models import Task
from todo.forms import TaskUpdateForm

class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description']  
    template_name = 'todo/todo_create.html'
    success_url = reverse_lazy('todo:task_list')

    def form_valid(self, form):
        form.instance.user = self.request.user.profile 
        return super(TaskCreate, self).form_valid(form)

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = "task"
    success_url = reverse_lazy("todo:task_list")

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user.profile)

class TaskUpdateView(LoginRequiredMixin,UpdateView):
    model = Task
    success_url = reverse_lazy("todo:task_list")
    form_class = TaskUpdateForm
    template_name = "todo/todo_edit.html"

class TaskToggelView(LoginRequiredMixin,View):
    

    def post(self, request, pk, *args, **kwargs):
        task = Task.objects.get(pk=pk,user=self.request.user.profile)
        task.complete = not task.complete
        task.save()
        return redirect("todo:task_list")

class TaskDetailView(LoginRequiredMixin,DetailView):
    model = Task
    template_name = "todo/todo_detail.html"
    context_object_name = "todo"

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user.profile)
    

class TaskList(LoginRequiredMixin,ListView):
    model = Task
    context_object_name = "tasks"
    template_name = "todo/todo_list.html"

    def get_queryset(self):
       return Task.objects.filter(user=self.request.user.profile)

