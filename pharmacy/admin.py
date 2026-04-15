
# Register your models here.
# pharmacy/admin.py
# Register models so they appear in Django's built-in admin panel at /admin/

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Medicine, Category, Bill, BillItem


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock_quantity', 'expiry_date', 'manufacturer']
    list_filter = ['category', 'expiry_date']
    search_fields = ['name', 'manufacturer']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']


class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 0


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['bill_number', 'customer_name', 'pharmacist', 'total_amount', 'created_at']
    inlines = [BillItemInline]
    list_filter = ['status', 'created_at']


