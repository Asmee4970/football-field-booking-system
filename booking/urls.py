from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),

    path('home/', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),

    path('my-booking/', views.my_booking, name='my_booking'),

    path('field/<int:field_id>/', views.field_detail, name='field_detail'),
    path('booking/', views.booking, name='booking'),
    path("create-booking/", views.create_booking, name="create_booking"),
    path('payment/', views.payment, name='payment'),

    # ✅ เหลืออันเดียวพอ
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/fields/', views.field_management, name='field_management'),
    path('dashboard/bookings/', views.booking_management, name='booking_management'),
]
