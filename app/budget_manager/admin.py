from django.contrib import admin
from .models import Expenses, ExpensesCategory, Store, AppUser
from django.contrib.auth.admin import UserAdmin


admin.site.register(AppUser, UserAdmin)
admin.site.register(Expenses)
admin.site.register(ExpensesCategory)
admin.site.register(Store)
