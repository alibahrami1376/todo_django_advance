# گزارش کامل ایرادهای پروژه Todo Advance

این فایل شامل تمام ایرادها، مشکلات امنیتی و پیشنهادات بهبود پروژه است.

---

## 🔴 مشکلات امنیتی (Critical)

### 1. **TaskToggelView - استفاده از `.get()` بدون Exception Handling**
**فایل:** `todo/views.py` - خط 46

**مشکل:**
```python
task = Task.objects.get(pk=pk,user=self.request.user.profile)
```

**خطر:** اگر task با این pk و user پیدا نشود، `DoesNotExist` exception رخ می‌دهد و صفحه 500 error می‌دهد.

**راه حل:**
```python
from django.shortcuts import get_object_or_404

def post(self, request, pk, *args, **kwargs):
    task = get_object_or_404(Task, pk=pk, user=self.request.user.profile)
    task.complete = not task.complete
    task.save()
    return redirect("todo:task_list")
```

---

### 2. **TaskUpdateView - عدم وجود get_queryset برای امنیت**
**فایل:** `todo/views.py` - خط 36-40

**مشکل:** 
`TaskUpdateView` متد `get_queryset()` ندارد، بنابراین کاربران می‌توانند task های دیگران را ویرایش کنند.

**راه حل:**
```python
class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    success_url = reverse_lazy("todo:task_list")
    form_class = TaskUpdateForm
    template_name = "todo/todo_edit.html"
    
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user.profile)
```

---

### 3. **SECRET_KEY در settings.py Hardcoded است**
**فایل:** `core/settings.py` - خط 23

**مشکل:**
```python
SECRET_KEY = 'django-insecure-hew^m)@68ko$ezaf0vp4%!4qvtqpz*_t1hr%s8zdn$%-ypm&u('
```

**خطر:** این کلید در کد commit شده و برای production خطرناک است.

**راه حل:**
- استفاده از environment variables
- استفاده از `python-decouple` یا `django-environ`
- اضافه کردن `.env` به `.gitignore`

---

### 4. **DEBUG = True و ALLOWED_HOSTS خالی**
**فایل:** `core/settings.py` - خط 26, 28

**مشکل:**
```python
DEBUG = True
ALLOWED_HOSTS = []
```

**راه حل:**
```python
import os
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
```

---

## 🟡 مشکلات کدنویسی (Code Issues)

### 5. **Typo در نام کلاس: TaskToggelView**
**فایل:** `todo/views.py` - خط 42

**مشکل:** نام کلاس `TaskToggelView` است که باید `TaskToggleView` باشد.

**تأثیر:** در `todo/urls.py` هم استفاده شده و باید همه جا تغییر کند.

---

### 6. **Typo در نام کلاس: CustoumLogoutView**
**فایل:** `accounts/views.py` - خط 35

**مشکل:** نام کلاس `CustoumLogoutView` است که باید `CustomLogoutView` باشد.

**تأثیر:** در `accounts/urls.py` هم استفاده شده.

---

### 7. **Import نادرست در views.py**
**فایل:** `todo/views.py` - خط 13

**مشکل:**
```python
from todo.forms import TaskUpdateForm
```

**بهتر است:**
```python
from .forms import TaskUpdateForm
```

---

### 8. **Import نادرست در core/urls.py**
**فایل:** `core/urls.py` - خط 18

**مشکل:**
```python
from core import settings
```

**باید:**
```python
from django.conf import settings
```

---

### 9. **Indentation اشتباه در TaskCreate.form_valid**
**فایل:** `todo/views.py` - خط 21-23

**مشکل:** در کد فعلی indentation درست است، اما باید بررسی شود که `form.instance.user` به درستی set می‌شود.

**نکته:** کد فعلی درست است، اما بهتر است بررسی شود که `self.request.user.profile` همیشه وجود دارد.

---

### 10. **Profile.description بدون blank=True**
**فایل:** `accounts/models.py` - خط 77

**مشکل:**
```python
description = models.TextField()
```

**راه حل:**
```python
description = models.TextField(blank=True, null=True)
```

چون در signal هنگام ایجاد Profile، description set نمی‌شود و ممکن است خطا بدهد.

---

## 🟠 مشکلات Template

### 11. **فیلدهای غیرموجود در Model در Template استفاده شده**
**فایل:** `templates/todo/todo_edit.html` و `templates/todo/todo_detail.html`

**مشکل:** 
Template ها از فیلدهای زیر استفاده می‌کنند که در مدل `Task` وجود ندارند:
- `priority` (خط 65-81 در todo_edit.html)
- `status` (خط 84-102 در todo_edit.html)
- `due_date` (خط 105-121 در todo_edit.html)
- `completed` (خط 41, 87 در todo_detail.html)
- `created_at` (خط 58 در todo_detail.html)
- `updated_at` (خط 60 در todo_detail.html)

**راه حل:**
- یا این فیلدها را به مدل اضافه کنید
- یا از template حذف کنید

**نکته:** در مدل فعلی `complete` وجود دارد نه `completed`، و `created_date` وجود دارد نه `created_at`.

---

### 12. **متن اضافی "description" در todo_edit.html**
**فایل:** `templates/todo/todo_edit.html` - خط 8

**مشکل:**
```html
<div class="form-header">description
```

**راه حل:**
```html
<div class="form-header">
```

---

### 13. **لینک خالی در todo_edit.html**
**فایل:** `templates/todo/todo_edit.html` - خط 10

**مشکل:**
```html
<a href="" class="btn-back">← Back</a>
```

**راه حل:**
```html
<a href="{% url 'todo:task_list' %}" class="btn-back">← Back</a>
```

---

### 14. **استفاده از فیلدهای اشتباه در todo_detail.html**
**فایل:** `templates/todo/todo_detail.html`

**مشکل:**
- خط 58: `{{ todo.created_at|date:"Y/m/d H:i" }}` باید `{{ todo.created_date|date:"Y/m/d H:i" }}` باشد
- خط 63: `{{ todo.updated_at|date:"Y/m/d H:i" }}` باید `{{ todo.updated_date|date:"Y/m/d H:i" }}` باشد
- خط 41, 87: `todo.completed` باید `todo.complete` باشد

---

## 🔵 مشکلات URL و Routing

### 15. **Typo در URL: "toggel"**
**فایل:** `todo/urls.py` - خط 19

**مشکل:**
```python
path("toggel/<int:pk>/", TaskToggelView.as_view(), name="toggel_task"),
```

**بهتر است:**
```python
path("toggle/<int:pk>/", TaskToggleView.as_view(), name="toggle_task"),
```

---

## 🟢 پیشنهادات بهبود (Best Practices)

### 16. **استفاده از get_object_or_404 به جای get()**
همیشه از `get_object_or_404` استفاده کنید تا خطاهای 500 به 404 تبدیل شوند.

---

### 17. **اضافه کردن get_queryset به همه View ها**
برای امنیت، همه View هایی که با object کار می‌کنند باید `get_queryset()` داشته باشند.

---

### 18. **استفاده از Messages Framework**
برای نمایش پیام‌های موفقیت/خطا به کاربر، از Django Messages Framework استفاده کنید.

**مثال:**
```python
from django.contrib import messages

messages.success(self.request, 'Task created successfully!')
```

---

### 19. **اضافه کردن Validation به Forms**
در فرم‌ها validation بیشتری اضافه کنید.

---

### 20. **استفاده از Class-based Views بهتر**
برخی View ها می‌توانند ساده‌تر شوند.

---

### 21. **اضافه کردن Tests**
هیچ test فایلی وجود ندارد. بهتر است unit tests و integration tests اضافه شود.

---

### 22. **مدیریت بهتر Static Files**
در settings.py کدهای comment شده وجود دارد که باید پاک شود.

---

### 23. **اضافه کردن .gitignore**
اگر وجود ندارد، باید فایل `.gitignore` اضافه شود تا فایل‌های غیرضروری commit نشوند.

---

### 24. **مدیریت بهتر Exception Handling**
در ProfileView از bare `except:` استفاده شده که خوب نیست.

**فایل:** `accounts/views.py` - خط 48

**مشکل:**
```python
except:
    profile = None
```

**بهتر:**
```python
except Profile.DoesNotExist:
    profile = None
```

---

### 25. **اضافه کردن Meta Class به Task Model**
می‌توانید ordering و verbose_name اضافه کنید:

```python
class Meta:
    order_with_respect_to = "user"
    ordering = ['-created_date']
    verbose_name = "Task"
    verbose_name_plural = "Tasks"
```

---

## 📋 خلاصه اولویت‌ها

### فوری (Critical):
1. اضافه کردن `get_queryset()` به `TaskUpdateView`
2. استفاده از `get_object_or_404` در `TaskToggelView`
3. اصلاح import در `core/urls.py`
4. حذف فیلدهای غیرموجود از template ها یا اضافه کردن به مدل

### مهم (High):
5. اصلاح typo ها (TaskToggelView, CustoumLogoutView)
6. اصلاح فیلدهای template (created_at → created_date, completed → complete)
7. اضافه کردن blank=True به Profile.description
8. اصلاح لینک خالی در todo_edit.html

### متوسط (Medium):
9. استفاده از environment variables برای SECRET_KEY
10. اضافه کردن exception handling بهتر
11. اضافه کردن tests
12. پاک کردن کدهای comment شده

---

**تاریخ بررسی:** 2025-12-28
**نسخه Django:** 3.2.25

