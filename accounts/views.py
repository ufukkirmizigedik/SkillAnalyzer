from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404
from .models import CustomUser
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_decode
# Kullanıcı girişi
def login_view(request):
    if request.user.is_authenticated:  # Kullanıcı zaten giriş yaptıysa
        return redirect('dashboard')  # Dashboard sayfasına yönlendir

    form = AuthenticationForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('dashboard')
    elif request.method == 'POST':
        messages.error(request, "Неправильное имя пользователя или пароль.")

    return render(request, 'accounts/login.html', {'form': form})

# Kullanıcı çıkışı
def logout_view(request):
    logout(request)
    messages.success(request, "Вы успешно вышли из системы.")
    return redirect('login')

# Dashboard
@login_required
def dashboard(request):
    user = request.user
    return render(request, 'accounts/dashboard.html', {
        'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
        'credits': user.analysis_credits,
        'is_active_member': user.is_active_member,
    })


# Dosya yükleme
@login_required
def upload_file(request):
    user = request.user

    if not user.is_active_member or user.analysis_credits <= 0:
        messages.error(request, "У вас больше нет прав на анализ. Пожалуйста, пополните ваш баланс.")
        return redirect('dashboard')

    if request.method == 'POST' and request.FILES.get('jupyter_file'):
        uploaded_file = request.FILES['jupyter_file']

        try:
            content = uploaded_file.read().decode('utf-8')
            word_count = len(content.split())  # Basit analiz
            result = f"Ваш файл содержит {word_count} слов."  # Analiz sonucu

            # Kullanıcının analiz hakkını azalt
            user.analysis_credits -= 1
            if user.analysis_credits == 0:
                user.is_active_member = False
            user.save()  # Değişiklikleri kaydet

            # Sonucu session'a kaydet ve yönlendir
            request.session['analysis_result'] = result
            messages.success(request, f"Ваш файл проанализирован. Осталось прав: {user.analysis_credits}")
            return redirect('result')

        except Exception as e:
            messages.error(request, f"Произошла ошибка при анализе файла: {str(e)}")
            return redirect('upload')

    return render(request, 'accounts/upload.html')




# CSRF hata mesajı
def csrf_failure(request, reason=""):
    return render(request, 'accounts/csrf_failure.html', {'reason': reason})


@login_required
def result_view(request):
    result = request.session.get('analysis_result', None)
    if not result:
        messages.error(request, "Результаты анализа недоступны. Попробуйте снова загрузить файл.")
        return redirect('upload')

    return render(request, 'accounts/result.html', {'result': result})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Kullanıcıyı hemen kaydetme, değişiklik yapacağız
            user.is_active = False  # Kullanıcı başlangıçta aktif değil
            user.save()

            # E-posta doğrulama bağlantısını gönder
            send_verification_email(user, request)

            # Kullanıcıya bilgilendirme mesajı
            messages.success(request, f"Добро пожаловать, {user.username}! Подтверждение отправлено на ваш адрес электронной почты: {user.email}")

            # Bilgilendirme sayfasına yönlendirme
            return render(request, 'accounts/verification_sent.html')  # Kullanıcıyı bilgi ekranına yönlendir
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})




def send_verification_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verification_link = f"{request.scheme}://{request.get_host()}/accounts/verify/{uid}/{token}/"

    send_mail(
        subject="Подтверждение учетной записи",
        message=f"Здравствуйте, {user.username}!\n\nПожалуйста, подтвердите ваш аккаунт, перейдя по ссылке:\n{verification_link}",
        from_email='your-email@gmail.com',
        recipient_list=[user.email],
        fail_silently=False,
    )




def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True  # Kullanıcıyı aktif yap
        user.is_active_member = True  # Kullanıcıyı aktif üye yap
        user.analysis_credits = 1  # Başlangıç analiz hakkını ver
        user.save()
        return render(request, 'accounts/verification_success.html')  # Başarılı doğrulama sayfası
    else:
        return render(request, 'accounts/verification_failed.html')  # Başarısız doğrulama sayfası
