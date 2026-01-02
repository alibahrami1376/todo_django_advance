# گزارش امنیتی Todo App

## ✅ موارد امنیتی که به درستی پیاده‌سازی شده‌اند:

### 1. **Views (todo/views.py)**
- ✅ **TaskListView** (خط 88-89): فیلتر بر اساس `user=self.request.user.profile`
- ✅ **TaskDetailView** (خط 77-78): فیلتر بر اساس `user=self.request.user.profile`
- ✅ **TaskUpdateView** (خط 56-57): فیلتر بر اساس `user=self.request.user.profile`
- ✅ **TaskDeleteView** (خط 43-44): فیلتر بر اساس `user=self.request.user.profile`
- ✅ **TaskToggleView** (خط 64): استفاده از `get_object_or_404` با فیلتر `user=self.request.user.profile`
- ✅ **TaskCreateView** (خط 27): تنظیم خودکار `user` به `request.user.profile`

**نتیجه**: کاربران فقط می‌توانند task های خودشان را ببینند، ویرایش کنند و حذف کنند.

---

## 🔴 مشکلات امنیتی بحرانی:

### 1. **Admin Panel (todo/admin.py)**
**مشکل**: هیچ محدودیتی در admin panel وجود ندارد!
- ❌ Superuser می‌تواند **همه** task های همه کاربران را ببیند
- ❌ Superuser می‌تواند task های دیگران را ویرایش و حذف کند
- ❌ هیچ فیلتری بر اساس user وجود ندارد

**راه حل**: باید یک `ModelAdmin` سفارشی با `get_queryset` اضافه شود:

```python
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user.profile)
```

### 2. **Model Task (todo/models.py)**
**مشکل**: فیلد `user` می‌تواند `null=True` باشد!
- ❌ خط 6: `null=True, blank=True` - این اجازه می‌دهد task بدون user ایجاد شود
- ❌ این می‌تواند باعث شود task هایی بدون owner ایجاد شوند

**راه حل**: باید `null=False` شود (البته باید migration ایجاد شود):

```python
user = models.ForeignKey(
    "accounts.Profile", 
    on_delete=models.CASCADE, 
    null=False,  # تغییر این
    blank=False  # تغییر این
)
```

### 3. **عدم بررسی وجود Profile**
**مشکل**: در تمام views، اگر `request.user.profile` وجود نداشته باشد، `AttributeError` رخ می‌دهد.

**مثال**:
- خط 27: `form.instance.user = self.request.user.profile` 
- خط 44: `self.model.objects.filter(user=self.request.user.profile)`
- خط 57: `self.model.objects.filter(user=self.request.user.profile)`
- خط 64: `get_object_or_404(Task,pk=pk,user=self.request.user.profile)`
- خط 78: `self.model.objects.filter(user=self.request.user.profile)`
- خط 89: `Task.objects.filter(user=self.request.user.profile)`

**راه حل**: باید بررسی شود:
```python
if not hasattr(self.request.user, 'profile'):
    return Task.objects.none()
```

---

## 🟡 مشکلات امنیتی متوسط:

### 1. **عدم استفاده از Permission Classes اضافی**
- فقط `LoginRequiredMixin` استفاده شده که کافی است
- اما می‌توان یک Mixin سفارشی برای بررسی profile اضافه کرد

### 2. **عدم بررسی در Serializer (اگر API وجود داشته باشد)**
- اگر API views وجود داشته باشد، باید permission classes و queryset filtering بررسی شود

---

## 📋 خلاصه:

| بخش | وضعیت | مشکل |
|-----|-------|------|
| Views (List/Detail/Update/Delete) | ✅ امن | - |
| Views (Create/Toggle) | ✅ امن | - |
| Admin Panel | 🔴 **ناسالم** | Superuser همه task ها را می‌بیند |
| Model Task | 🟡 **خطرناک** | user می‌تواند null باشد |
| بررسی Profile | 🟡 **خطرناک** | اگر profile نباشد خطا می‌دهد |

---

## 🎯 اولویت رفع مشکلات:

1. **🔴 فوری**: محدود کردن Admin Panel
2. **🔴 فوری**: تغییر Model برای جلوگیری از null user
3. **🟡 مهم**: اضافه کردن بررسی وجود profile در views

---

## ✅ نتیجه‌گیری:

**Views به درستی محدود شده‌اند** و کاربران فقط task های خودشان را می‌بینند. اما **Admin Panel و Model** نیاز به اصلاح دارند.

