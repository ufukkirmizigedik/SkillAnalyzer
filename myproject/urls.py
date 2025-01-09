from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
def redirect_to_login(request):
    return redirect('login')

def redirect_to_register(request):
    return redirect('register')  # 'register' URL'sine yönlendir

urlpatterns = [
    path('ufuk-ben-admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # accounts/views.py kullanılır
    path('app/', include('app.urls')),           # app/views.py kullanılır
    path('', redirect_to_register),  # Ana sayfa login'e yönlendirir
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)