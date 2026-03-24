from django.contrib import admin
from .models import Field, Booking, Payment
# Register your models here.

@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ("name", "field_type", "price", "open_time", "close_time")

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "field", "date", "start_time", "end_time", "status", "is_walkin")
    list_filter = ("status", "is_walkin", "date", "field")
    search_fields = ("user__username", "field__name")

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("booking", "status", "uploaded_at")