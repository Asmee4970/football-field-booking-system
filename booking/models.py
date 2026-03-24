from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# Field
FIELD_TYPE = (
    ('football', 'ฟุตบอล'),
    ('futsal', 'ฟุตซอล'),
    ('football7', 'หญ้าเทียม'),
)

class Field(models.Model):
    name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE)
    price = models.IntegerField()
    image = models.ImageField(upload_to='fields/', null=True, blank=True)
    open_time = models.TimeField()
    close_time = models.TimeField()
    
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# Booking
class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    field = models.ForeignKey(Field, on_delete=models.SET_NULL, null=True, blank=True)

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    hours = models.IntegerField()
    total_price = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    slip = models.ImageField(upload_to="slips/", null=True, blank=True)
    is_walkin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    hours = models.IntegerField()
    water_packs = models.IntegerField(default=0)
    balls = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.water_packs = self.hours * 2
            self.balls = 2
            
        super().save(*args, **kwargs)

    def __str__(self):
        username = self.user.username if self.user else "ผู้ใช้ที่ถูกลบ"
        field_name = self.field.name if self.field else "สนามที่ถูกลบ"
        return f"{username} - {field_name}"

    class Meta:
        ordering = ['-created_at']

# Payment
class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)
    slip = models.ImageField(upload_to="slips/", null=True, blank=True)
    status = models.CharField(max_length=20, default="pending")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.booking if self.booking else 'Deleted Booking'}"

# Profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username


# Email OTP
class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)


# views.py
def booking_management(request):
    fields = Field.objects.all()
    bookings = Booking.objects.all()
    return render(request, 'your_template.html', {
        'fields': fields, 
        'bookings': bookings
    })