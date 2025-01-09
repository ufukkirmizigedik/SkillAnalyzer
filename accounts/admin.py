from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class CustomUserAdmin(BaseUserAdmin):
    # Görüntülenecek alanlar
    list_display = ('username', 'email', 'is_active', 'is_active_member', 'analysis_credits')
    list_filter = ('is_active', 'is_active_member')

    # Kullanıcı detayları
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_active_member')}),
        (_('Analysis Info'), {'fields': ('analysis_credits',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    # Kullanıcı ekleme ekranı
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active_member', 'analysis_credits'),
        }),
    )

    # Arama ve sıralama
    search_fields = ('username', 'email')
    ordering = ('username',)

    # Şifre değiştirme için özel metod
    def get_fieldsets(self, request, obj=None):
        if not obj:  # Yeni bir kullanıcı ekliyorsanız
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)


# CustomUser modelini kaydet
admin.site.register(CustomUser, CustomUserAdmin)
