from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_file, name='upload'),
    path('result/', views.result_view, name='result'),
    path('register/', views.register, name='register'),
    path('verify/<uidb64>/<token>/', views.verify_email, name='verify_email')# Yeni yönlendirme
]
