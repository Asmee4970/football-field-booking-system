from django.urls import path
from . import views

urlpatterns = [

    # หน้าเริ่มต้น
    path('', views.welcome, name='welcome'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),

    # Email Verify
    path('verify-email/', views.verify_email, name='verify_email'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),

    # User pages
    path('home/', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('my-booking/', views.my_booking, name='my_booking'),
    path('edit-profile-success/', views.edit_profile_success, name='edit_profile_success_page'),

    # Booking flow
    path('field/<int:field_id>/', views.field_detail, name='field_detail'),
    path('booking/', views.booking_page, name='booking'),
    path('create-booking/<int:field_id>/', views.booking_create, name='create_booking'),
    path('payment/<int:booking_id>/', views.payment, name='payment'),
    path('upload-slip/<int:booking_id>/', views.upload_slip, name='upload_slip'),

    # Admin dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Field management
    path('dashboard/fields/', views.field_management, name='field_management'),
    path('dashboard/fields/edit/<int:id>/', views.edit_field, name='edit_field'),
    path('dashboard/fields/delete/<int:field_id>/', views.delete_field, name='delete_field'),

    # Booking management
    path('dashboard/bookings/', views.booking_management, name='booking_management'),
    path('approve-booking/<int:booking_id>/', views.approve_booking, name='approve_booking'),
    path('reject-booking/<int:booking_id>/', views.reject_booking, name='reject_booking'),
    path("dashboard/bookings/cancel/<int:booking_id>/",views.cancel_booking,name="cancel_booking"),

]