from django.shortcuts import redirect

class RestrictAdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Admin paneline erişim isteklerini kontrol et
        if request.path.startswith('/admin/') and request.user.is_authenticated:
            # Eğer kullanıcı staff değilse admin paneline erişim reddedilir
            if not request.user.is_staff:
                return redirect('login')  # Login sayfasına yönlendir
        return self.get_response(request)
