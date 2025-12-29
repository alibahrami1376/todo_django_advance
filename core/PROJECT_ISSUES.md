# گزارش کامل ایرادهای پروژه Todo Advance

این فایل شامل تمام ایرادها، مشکلات امنیتی و پیشنهادات بهبود پروژه است.

**آخرین به‌روزرسانی:** 2025-12-28

---

## ✅ مشکلات حل شده

### 1. ✅ **TaskToggleView - استفاده از get_object_or_404**
**وضعیت:** حل شده  
**فایل:** `todo/views.py` - خط 49

کد فعلی:
```python
task = get_object_or_404(Task, pk=pk, user=self.request.user.profile)
```

---

### 2. ✅ **TaskUpdateView - اضافه شدن get_queryset**
**وضعیت:** حل شده  
**فایل:** `todo/views.py` - خط 43-44

کد فعلی:
```python
def get_queryset(self):
    return self.model.objects.filter(user=self.request.user.profile)
```

---

### 3. ✅ **اصلاح Import در core/urls.py**
**وضعیت:** حل شده  
**فایل:** `core/urls.py` - خط 18

کد فعلی:
```python
from django.conf import settings
```

---

### 4. ✅ **اصلاح Typo: TaskToggelView → TaskToggleView**
**وضعیت:** حل شده  
**فایل:** `todo/views.py` - خط 46

---

### 5. ✅ **اصلاح Typo: CustoumLogoutView → CustomLogoutView**
**وضعیت:** حل شده  
**فایل:** `accounts/views.py` - خط 35

---

### 6. ✅ **اصلاح URL: toggel → toggle**
**وضعیت:** حل شده  
**فایل:** `todo/urls.py` - خط 19

کد فعلی:
```python
path("toggle/<int:pk>/", TaskToggleView.as_view(), name="toggle_task"),
```

---

### 7. ✅ **حذف فیلدهای غیرموجود از Template ها**
**وضعیت:** حل شده  
**فایل:** `templates/todo/todo_edit.html` و `templates/todo/todo_detail.html`

- فیلدهای `priority`, `status`, `due_date` از template ها حذف شدند
- فیلدهای `completed` به `complete` تغییر یافتند
- فیلدهای `created_at` به `created_date` تغییر یافتند
- فیلدهای `updated_at` به `updated_date` تغییر یافتند

---

### 8. ✅ **اصلاح متن اضافی و لینک خالی در todo_edit.html**
**وضعیت:** حل شده  
**فایل:** `templates/todo/todo_edit.html`

- متن اضافی "description" حذف شد
- لینک خالی به `{% url 'todo:task_list' %}` تغییر یافت

---

### 9. ✅ **اضافه کردن blank=True به Profile.description**
**وضعیت:** حل شده  
**فایل:** `accounts/models.py` - خط 77

کد فعلی:
```python
description = models.TextField(blank=True, null=True)
```

---

## 🔴 مشکلات امنیتی باقی مانده (Critical)

### 1. **SECRET_KEY در settings.py Hardcoded است**
**فایل:** `core/settings.py` - خط 23

**مشکل:**
```python
SECRET_KEY = 'django-insecure-hew^m)@68ko$ezaf0vp4%!4qvtqpz*_t1hr%s8zdn$%-ypm&u('
```

**خطر:** این کلید در کد commit شده و برای production خطرناک است.

**راه حل:**
```python
import os
from decouple import config

SECRET_KEY = config('SECRET_KEY', default='django-insecure-...')
```

یا:
```python
import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-...')
```

**نکته:** باید فایل `.env` ایجاد شود و به `.gitignore` اضافه شود.

---

### 2. **DEBUG = True و ALLOWED_HOSTS خالی**
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
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',') if os.environ.get('ALLOWED_HOSTS') else []
```

---

## 🟡 مشکلات کدنویسی باقی مانده (Code Issues)

### 1. **Import نادرست در views.py**
**فایل:** `todo/views.py` - خط 14

**مشکل:**
```python
from todo.forms import TaskUpdateForm
```

**بهتر است:**
```python
from .forms import TaskUpdateForm
```

**دلیل:** استفاده از relative import بهتر است و از circular import جلوگیری می‌کند.

---

### 2. **Profile Signal - مشکل در ایجاد Profile**
**فایل:** `accounts/models.py` - خط 85-91

**مشکل:**
```python
@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
```

**خطر:** فیلدهای `first_name` و `last_name` در مدل Profile required هستند اما در signal set نمی‌شوند. این باعث خطا می‌شود.

**راه حل:**
```python
@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(
            user=instance,
            defaults={
                'first_name': '',
                'last_name': '',
            }
        )
```

یا بهتر است فیلدها را optional کنید:
```python
first_name = models.CharField(max_length=250, blank=True)
last_name = models.CharField(max_length=250, blank=True)
```

---

### 3. **Exception Handling در ProfileView**
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

**دلیل:** استفاده از bare `except:` همه exception ها را catch می‌کند که خطرناک است.

---

### 4. **عدم بررسی وجود Profile در TaskCreate**
**فایل:** `todo/views.py` - خط 23

**مشکل:**
```python
form.instance.user = self.request.user.profile
```

**خطر:** اگر profile وجود نداشته باشد، `AttributeError` رخ می‌دهد.

**راه حل:**
```python
def form_valid(self, form):
    try:
        form.instance.user = self.request.user.profile
    except Profile.DoesNotExist:
        # ایجاد profile اگر وجود نداشته باشد
        Profile.objects.create(user=self.request.user, first_name='', last_name='')
        form.instance.user = self.request.user.profile
    return super(TaskCreate, self).form_valid(form)
```

یا بهتر است middleware یا signal اضافه کنید که همیشه profile وجود داشته باشد.

---

## 🟠 مشکلات Template

### 1. **کدهای Comment شده در settings.py**
**فایل:** `core/settings.py` - خط 123-124, 137-139

**مشکل:** کدهای comment شده باید پاک شوند یا اگر نیاز است، توضیح داده شوند.

**راه حل:** کدهای comment شده را پاک کنید یا اگر برای reference هستند، توضیح اضافه کنید.

---

## 🟢 پیشنهادات بهبود (Best Practices)

### 1. **استفاده از Messages Framework**
برای نمایش پیام‌های موفقیت/خطا به کاربر، از Django Messages Framework استفاده کنید.

**مثال:**
```python
from django.contrib import messages

def form_valid(self, form):
    messages.success(self.request, 'Task created successfully!')
    return super().form_valid(form)
```

---

### 2. **اضافه کردن Validation به Forms**
در فرم‌ها validation بیشتری اضافه کنید.

**مثال:**
```python
def clean_title(self):
    title = self.cleaned_data.get('title')
    if len(title) < 3:
        raise forms.ValidationError("Title must be at least 3 characters.")
    return title
```

---

### 3. **اضافه کردن Tests**
هیچ test فایلی وجود ندارد. بهتر است unit tests و integration tests اضافه شود.

**پیشنهاد:**
- تست ایجاد Task
- تست ویرایش Task
- تست حذف Task
- تست امنیت (کاربر نمی‌تواند task دیگران را ویرایش کند)

---

### 4. **اضافه کردن .gitignore**
فایل `.gitignore` وجود ندارد.

**محتویات پیشنهادی:**
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
/media
/staticfiles

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
```

---

### 5. **اضافه کردن Meta Class به Task Model**
می‌توانید ordering و verbose_name اضافه کنید:

```python
class Meta:
    order_with_respect_to = "user"
    ordering = ['-created_date']
    verbose_name = "Task"
    verbose_name_plural = "Tasks"
    indexes = [
        models.Index(fields=['user', '-created_date']),
    ]
```

---

### 6. **اضافه کردن __str__ بهتر به Profile**
**فایل:** `accounts/models.py` - خط 81

**پیشنهاد:**
```python
def __str__(self):
    if self.first_name or self.last_name:
        return f"{self.first_name} {self.last_name}".strip()
    return self.user.email
```

---

### 7. **استفاده از get_object_or_404 در همه جا**
همیشه از `get_object_or_404` استفاده کنید تا خطاهای 500 به 404 تبدیل شوند.

**نکته:** این کار در TaskToggleView انجام شده است ✅

---

### 8. **اضافه کردن Pagination به TaskList**
اگر تعداد task ها زیاد شود، بهتر است pagination اضافه شود.

**راه حل:**
```python
class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = "tasks"
    template_name = "todo/todo_list.html"
    paginate_by = 10  # اضافه کردن این خط
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user.profile)
```

---

### 9. **اضافه کردن Search و Filter**
در TaskList می‌توانید search و filter اضافه کنید.

**مثال:**
```python
def get_queryset(self):
    queryset = Task.objects.filter(user=self.request.user.profile)
    search = self.request.GET.get('search')
    if search:
        queryset = queryset.filter(title__icontains=search)
    status = self.request.GET.get('status')
    if status:
        queryset = queryset.filter(complete=(status == 'completed'))
    return queryset
```

**نکته:** در template فعلی فیلترها وجود دارند اما در view پیاده‌سازی نشده‌اند.

---

### 10. **استفاده از reverse_lazy به جای hardcoded URLs**
در برخی جاها از hardcoded URL استفاده شده است.

**مثال:**
```python
# بد
success_url = "/"

# خوب
success_url = reverse_lazy('todo:task_list')
```

---

## 📋 خلاصه اولویت‌ها

### فوری (Critical) - باید فوراً حل شوند:
1. ✅ ~~اضافه کردن `get_queryset()` به `TaskUpdateView`~~ (حل شده)
2. ✅ ~~استفاده از `get_object_or_404` در `TaskToggleView`~~ (حل شده)
3. ✅ ~~اصلاح import در `core/urls.py`~~ (حل شده)
4. 🔴 **استفاده از environment variables برای SECRET_KEY**
5. 🔴 **تنظیم DEBUG و ALLOWED_HOSTS برای production**

### مهم (High) - باید در اسرع وقت حل شوند:
6. ✅ ~~اصلاح typo ها (TaskToggelView, CustoumLogoutView)~~ (حل شده)
7. ✅ ~~اصلاح فیلدهای template~~ (حل شده)
8. ✅ ~~اضافه کردن blank=True به Profile.description~~ (حل شده)
9. 🟡 **اصلاح import در todo/views.py**
10. 🟡 **اصلاح Profile Signal برای ایجاد Profile**
11. 🟡 **اصلاح Exception Handling در ProfileView**
12. 🟡 **بررسی وجود Profile در TaskCreate**

### متوسط (Medium) - بهتر است حل شوند:
13. 🟢 **اضافه کردن Messages Framework**
14. 🟢 **اضافه کردن Tests**
15. 🟢 **اضافه کردن .gitignore**
16. 🟢 **پاک کردن کدهای comment شده**
17. 🟢 **اضافه کردن Pagination**
18. 🟢 **پیاده‌سازی Search و Filter در TaskList**

---

## 📊 آمار مشکلات

- **مشکلات حل شده:** 9
- **مشکلات امنیتی باقی مانده:** 2
- **مشکلات کدنویسی باقی مانده:** 4
- **پیشنهادات بهبود:** 10

**درصد پیشرفت:** ~60%

---

**تاریخ بررسی:** 2025-12-28  
**نسخه Django:** 3.2.25  
**وضعیت کلی:** پروژه در وضعیت خوبی است اما نیاز به بهبودهای امنیتی و کدنویسی دارد.
