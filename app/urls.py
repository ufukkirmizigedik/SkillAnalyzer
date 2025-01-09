from django.urls import path
from . import views  # app/views.py'yi içe aktarır

urlpatterns = [
    path('upload/', views.upload_file, name='upload'),  # app/views.py'deki upload_file fonksiyonu
]
