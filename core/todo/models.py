from django.db import models
from django.urls import reverse

class Task(models.Model):
    user = models.ForeignKey(
        "accounts.Profile", on_delete=models.CASCADE, null=True, blank=True
    )
    description = models.TextField(blank=True)
    title = models.CharField(max_length=200)
    complete = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        order_with_respect_to = "user"
    
    def get_snippet(self):
        return self.description[0:5]

    def get_absolute_api_url(self):
        return reverse("todo:api-v1:task-detail", kwargs={"pk": self.pk})
