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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    hours = models.IntegerField()
    total_price = models.IntegerField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    slip = models.ImageField(upload_to="slips/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.field.name}"

    class Meta:
        ordering = ['-created_at']


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


# Payment
class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    slip = models.ImageField(upload_to="slips/", null=True, blank=True)
    status = models.CharField(max_length=20, default="pending")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.booking}"