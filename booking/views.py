from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import Booking, Field
from datetime import datetime


# PUBLIC PAGES

def welcome(request):
    return render(request, 'booking/welcome.html')


# REGISTER
def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "รหัสผ่านไม่ตรงกัน")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "ชื่อผู้ใช้นี้ถูกใช้แล้ว")
            return redirect('register')

        User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        messages.success(request, "สมัครสมาชิกสำเร็จ กรุณาเข้าสู่ระบบ")
        return redirect('login')

    return render(request, 'booking/register.html')


# LOGIN
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # ⭐ ตรงนี้คือส่วนสำคัญ
            if user.is_superuser:
                return redirect("admin_dashboard")
            else:
                return redirect("home")

        else:
            messages.error(request, "Username หรือ Password ไม่ถูกต้อง")
            return redirect("login")

    return render(request, "booking/login.html")


# LOGOUT
def logout_view(request):
    logout(request)
    return redirect('welcome')


# USER PAGES (LOGIN REQUIRED)

@login_required
def home(request):
    return render(request, 'booking/home.html')


@login_required
def profile(request):
    return render(request, 'booking/profile.html')



@login_required
def field_detail(request, field_id):
    return render(request, 'booking/field-detail.html', {
        'field_id': field_id
    })


# BOOKING
@login_required
def booking(request):
    field_id = request.GET.get('field')
    date = request.GET.get('date')
    start = request.GET.get('start')
    end = request.GET.get('end')
    hours = int(request.GET.get('hours', 1))

    field = Field.objects.get(id=field_id)

    total = field.price * hours

    context = {
        'field': field,
        'date': date,
        'start': start,
        'end': end,
        'hours': hours,
        'total': total,
    }

    return render(request, 'booking/booking.html', context)




def booking_page(request):
    field_id = request.GET.get("field")
    date = request.GET.get("date")
    start = request.GET.get("start")
    end = request.GET.get("end")
    hours = request.GET.get("hours")

    if not all([field_id, date, start, end, hours]):
        return redirect("home")

    try:
        hours = int(hours)
        field = Field.objects.get(id=field_id)
    except (ValueError, Field.DoesNotExist):
        return redirect("home")

    total = field.price * hours

    context = {
        "field": field,
        "date": date,
        "start": start,
        "end": end,
        "hours": hours,
        "total": total,
    }

    return render(request, "booking/booking.html", context)


def create_booking(request):
    if request.method == "POST":
        field_id = request.POST.get("field")
        date = request.POST.get("date")
        start = request.POST.get("start")
        end = request.POST.get("end")
        hours = int(request.POST.get("hours"))
        total = int(request.POST.get("total"))

        field = Field.objects.get(id=field_id)

        Booking.objects.create(
            user=request.user,
            field=field,
            date=date,
            start_time=start,
            end_time=end,
            hours=hours,
            total_price=total,
            status="pending"
        )

        return redirect("my_booking")


def my_booking(request):
    bookings = Booking.objects.filter(user=request.user).order_by("-date")
    return render(request, "booking/my-booking.html", {"bookings": bookings})


# PAYMENT
@login_required
def payment(request):
    field_id = request.GET.get("field")
    date = request.GET.get("date")
    start = request.GET.get("start")
    end = request.GET.get("end")
    hours = request.GET.get("hours")
    total = request.GET.get("total")

    context = {
        "field_id": field_id,
        "date": date,
        "start": start,
        "end": end,
        "hours": hours,
        "total": total,
    }

    return render(request, 'booking/payment.html', context)



# PROFILE MANAGEMENT

@login_required
def edit_profile(request):
    if request.method == "POST":
        request.user.first_name = request.POST.get("full_name")
        request.user.email = request.POST.get("email")
        request.user.save()
        messages.success(request, "อัปเดตข้อมูลสำเร็จ")
        return redirect("profile")

    return render(request, "booking/edit-profile.html")


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "เปลี่ยนรหัสผ่านสำเร็จ")
            return redirect("profile")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "booking/change-password.html", {"form": form})


# FORGOT PASSWORD

def forgot_password(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "รหัสผ่านไม่ตรงกัน")
            return redirect("forgot_password")

        try:
            user = User.objects.get(username=username)
            user.set_password(password1)
            user.save()
            messages.success(request, "เปลี่ยนรหัสผ่านสำเร็จ")
            return redirect("login")
        except User.DoesNotExist:
            messages.error(request, "ไม่พบผู้ใช้นี้")

    return render(request, "booking/forgot-password.html")


# ADMIN PAGES

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect("home")

# mock data ชั่วคราว (ไว้ก่อนทำ Model จริง)

    context = {
        "total_fields": 3,
        "today_bookings": 5,
        "today_income": 6400,
        "total_bookings": 128,
    }

    return render(request, "booking/admin-dashboard.html", context)


@login_required
def field_management(request):
    return render(request, 'booking/field-management.html')


@login_required
def booking_management(request):

    # mock data ชั่วคราว (ไว้ก่อนทำ Model จริง)
    bookings = [
        {
            "user": "พี่มี่",
            "field": "สนามฟุตบอลใหญ่",
            "date": "2 ก.พ. 2569",
            "time": "18:00 - 21:00",
            "hours": 3,
            "status": "waiting"
        },
        {
            "user": "เนีย",
            "field": "สนามฟุตซอล",
            "date": "3 ก.พ. 2569",
            "time": "20:00 - 22:00",
            "hours": 2,
            "status": "approved"
        }
    ]

    return render(request, 'booking/booking-management.html', {
        'bookings': bookings
    })
