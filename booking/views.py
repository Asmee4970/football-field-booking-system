import json, random, calendar
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailOTP
from .models import Booking, Field, Profile
from datetime import datetime
from django.utils import timezone
from django.db.models import Sum, Count
from datetime import timedelta, date
from django.db.models import Q

# PUBLIC PAGES

def welcome(request):
    return render(request, 'booking/welcome.html')

# REGISTER
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "รหัสผ่านไม่ตรงกัน")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "ชื่อผู้ใช้นี้ถูกใช้แล้ว")
            return redirect("register")

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            user.is_active = False
            user.save()

            user.profile.phone = phone
            user.profile.save()

            otp = str(random.randint(100000, 999999))

            request.session["email_otp"] = otp
            request.session["verify_user"] = username

            subject = "รหัสยืนยันการสมัครสมาชิก - Football Field Booking"
            message = f"สวัสดีคุณ {username},\n\nรหัส OTP สำหรับยืนยันอีเมลของคุณคือ: {otp}\n\nกรุณานำรหัสนี้ไปกรอกในหน้าเว็บไซต์เพื่อเปิดใช้งานบัญชีของคุณ"
            
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            messages.success(request, f"ส่ง OTP ไปที่ {email} เรียบร้อยแล้ว")
            return redirect("verify_otp")

        except Exception as e:
            if 'user' in locals():
                user.delete()
            print(f"Email Error: {e}")
            messages.error(request, "ไม่สามารถส่งอีเมลได้ กรุณาตรวจสอบอีเมลของคุณหรือลองอีกครั้งในภายหลัง")
            return redirect("register")

    return render(request, "booking/register.html")

def verify_email(request):
    if request.method == "POST":
        input_otp = request.POST.get("otp")
        session_otp = request.session.get("email_otp")

        if input_otp == session_otp:
            messages.success(request, "ยืนยันอีเมลสำเร็จ")
            return redirect("login")
        else:
            messages.error(request, "OTP ไม่ถูกต้อง")

    return render(request, "booking/verify_otp.html")

def verify_otp(request):
    if request.method == "POST":
        otp_input = request.POST.get("otp")
        session_otp = request.session.get("email_otp")
        username = request.session.get("verify_user")

        if otp_input == session_otp:
            try:
                user = User.objects.get(username=username)
                user.is_active = True
                user.save()

                del request.session["email_otp"]
                del request.session["verify_user"]

                messages.success(request, "ยืนยันตัวตนสำเร็จ! คุณสามารถเข้าสู่ระบบได้แล้ว")
                return redirect("login")
            except User.DoesNotExist:
                messages.error(request, "ไม่พบข้อมูลผู้ใช้ กรุณาสมัครใหม่อีกครั้ง")
                return redirect("register")
        else:
            messages.error(request, "รหัส OTP ไม่ถูกต้อง กรุณาลองใหม่")

    return render(request, "booking/verify_otp.html")

# LOGIN
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, "กรุณายืนยันอีเมลก่อน")
                return redirect("login")

            login(request, user)

            if user.is_superuser:
                return redirect("admin_dashboard")
            else:
                return redirect("home")
        else:
            messages.error(request, "Username หรือ Password ไม่ถูกต้อง")
            return redirect("login")

    return render(request, 'booking/login.html')

# LOGOUT
def logout_view(request):
    logout(request)
    return redirect('welcome')

# USER PAGES
@login_required
def home(request):
    fields = Field.objects.all()
    return render(request, 'booking/home.html', {
        'fields': fields
    })

@login_required
def profile(request):
    return render(request, "booking/profile.html", {
        "profile": request.user.profile
    })



@login_required
def field_detail(request, field_id):
    field = get_object_or_404(Field, id=field_id)
    bookings = Booking.objects.filter(
        field=field,
        status__in=["pending", "approved"]
    )
    context = {
        "field": field,
        "bookings": bookings
    }
    return render(request, "booking/field-detail.html", context)

# BOOKING
@login_required
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
    except ValueError:
        return redirect("home")

    field = get_object_or_404(Field, id=field_id)
  
    exist = Booking.objects.filter(
    field=field,
    date=date,
    start_time__lt=end,
    end_time__gt=start,
    status__in=["pending", "approved"] # เพิ่มบรรทัดนี้เข้าไป
    ).exists()

    if exist:
        messages.error(request, "ช่วงเวลานี้มีคนจองแล้ว")
        return redirect("field_detail", field.id)

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

@login_required
def booking_create(request, field_id):
    if request.method != "POST":
        return redirect("field_detail", field_id=field_id)

    date_str = request.POST.get("date")
    start_time = request.POST.get("start")
    end_time = request.POST.get("end")
    slip = request.FILES.get("slip")

    if not date_str or not start_time or not end_time:
        messages.error(request, "ข้อมูลการจองไม่ครบ กรุณาเลือกเวลาใหม่")
        return redirect("field_detail", field_id=field_id)

    field = get_object_or_404(Field, id=field_id)

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        messages.error(request, "รูปแบบวันที่ไม่ถูกต้อง")
        return redirect("field_detail", field_id=field_id)

    overlap = Booking.objects.filter(
        field=field,
        date=date,
        status__in=["pending", "approved"]
    ).filter(
        Q(start_time__lt=end_time) &
        Q(end_time__gt=start_time)
    )

    if overlap.exists():
        messages.error(request, "ช่วงเวลานี้ถูกจองแล้ว")
        return redirect("field_detail", field_id=field_id)

    t1 = datetime.strptime(start_time, "%H:%M")
    t2 = datetime.strptime(end_time, "%H:%M")
    hours = int((t2 - t1).seconds / 3600)

    if hours <= 0:
        messages.error(request, "เวลาไม่ถูกต้อง")
        return redirect("field_detail", field_id=field_id)

    total_price = hours * field.price

    booking = Booking.objects.create(
        user=request.user,
        field=field,
        date=date,
        start_time=start_time,
        end_time=end_time,
        hours=hours,
        total_price=total_price,
        slip=slip,
        status="pending"
    )

    messages.success(request, "จองสำเร็จ กรุณารอแอดมินตรวจสอบสลิป")
    return redirect("payment", booking_id=booking.id)

def my_booking(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-id') 
    return render(request, 'booking/my-booking.html', {
        'bookings': bookings
    })

# PAYMENT
@login_required
def payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    context = {
        "booking": booking,
        "field": booking.field,
        "date": booking.date,
        "start": booking.start_time,
        "end": booking.end_time,
        "hours": booking.hours,
        "total": booking.total_price,
    }
    return render(request, "booking/payment.html", context)

@login_required
def upload_slip(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == "POST":
        slip = request.FILES.get("slip")
        if slip:
            booking.slip = slip
            booking.status = "pending"
            booking.save()
    return redirect("my_booking")

# PROFILE MANAGEMENT
@login_required
def edit_profile(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        request.user.first_name = request.POST.get("full_name")
        request.user.email = request.POST.get("email")
        request.user.save()
        profile.phone = request.POST.get("phone")
        profile.save()
        return redirect('edit_profile_success_page')
    return render(request, "booking/edit-profile.html", {"profile": profile})

def edit_profile_success(request):
    return render(request, 'booking/edit-profile-success.html')

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

    today = timezone.now().date()
    start_of_month = today.replace(day=1)

    total_fields = Field.objects.count()
    today_bookings = Booking.objects.filter(date=today).count()
    today_income = Booking.objects.filter(date=today, status='approved').aggregate(total=Sum('total_price'))['total'] or 0
    month_income = Booking.objects.filter(date__gte=start_of_month, status='approved').aggregate(total=Sum('total_price'))['total'] or 0
    
    top_field_query = Booking.objects.values('field__name').annotate(count=Count('id')).order_by('-count').first()
    top_field_name = top_field_query['field__name'] if top_field_query else "ไม่มีข้อมูล"
    
    pending_bookings = Booking.objects.filter(status='pending').count()
    total_bookings = Booking.objects.count()
    
    rejected_count = Booking.objects.filter(status='rejected').count()
    cancel_rate = round((rejected_count / total_bookings * 100), 1) if total_bookings > 0 else 0

    days_7 = []
    income_7 = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        total = Booking.objects.filter(date=day, status='approved').aggregate(sum=Sum('total_price'))['sum'] or 0
        days_7.append(day.strftime("%d/%m"))
        income_7.append(float(total))

    days_30 = []
    income_30 = []
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        total = Booking.objects.filter(date=day, status='approved').aggregate(sum=Sum('total_price'))['sum'] or 0
        days_30.append(day.strftime("%d/%m"))
        income_30.append(float(total))

    latest_bookings = Booking.objects.select_related("field", "user").order_by("-id")[:5]

    context = {
        "total_fields": total_fields,
        "today_bookings": today_bookings,
        "today_income": today_income,
        "month_income": month_income,
        "top_field_name": top_field_name,
        "pending_bookings": pending_bookings,
        "total_bookings": total_bookings,
        "cancel_rate": cancel_rate,
        "latest_bookings": latest_bookings,
        "chart_labels": json.dumps(days_7),
        "chart_data": json.dumps(income_7),
        "month_labels": json.dumps(days_30),
        "month_data": json.dumps(income_30),
    }
    return render(request, "booking/admin-dashboard.html", context)

@login_required
def field_management(request):
    fields = Field.objects.all()
    if request.method == "POST":
        field_id = request.POST.get("field_id")
        field = get_object_or_404(Field, id=field_id) if field_id else Field()
        field.name = request.POST.get("name")
        field.field_type = request.POST.get("field_type")
        field.price = request.POST.get("price")
        field.open_time = request.POST.get("open_time")
        field.close_time = request.POST.get("close_time")
        if request.FILES.get("image"):
            field.image = request.FILES.get("image")
        field.save()
        return redirect("field_management")
    return render(request, "booking/field-management.html", {"fields": fields})

def edit_field(request, field_id):
    field = get_object_or_404(Field, id=field_id)
    if request.method == "POST":
        field.name = request.POST.get("name")
        field.field_type = request.POST.get("field_type")
        field.price = request.POST.get("price")
        field.open_time = request.POST.get("open_time")
        field.close_time = request.POST.get("close_time")
        if request.FILES.get("image"):
            field.image = request.FILES.get("image")
        field.save()
        return redirect("field_management")
    return render(request, "booking/edit_field.html", {"field": field})

def delete_field(request, field_id):
    field = get_object_or_404(Field, id=field_id)
    field.delete()
    return redirect("field_management")

@login_required
def booking_management(request):
    bookings = Booking.objects.select_related("user", "field").order_by("-created_at")
    return render(request, "booking/booking-management.html", {"bookings": bookings})

@login_required
def cancel_booking(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    booking.status = "cancelled"
    booking.save()
    return redirect("booking_management")

@login_required
def approve_booking(request, booking_id):
    if not request.user.is_superuser:
        return redirect("home")
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = "approved"
    booking.save()
    return redirect("booking_management")

@login_required
def reject_booking(request, booking_id):
    if not request.user.is_superuser:
        return redirect("home")
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = "rejected"
    booking.save()
    return redirect("booking_management")