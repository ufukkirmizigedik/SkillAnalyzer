import os
from openai import OpenAI
from django.shortcuts import render,redirect
from django.conf import settings
import tiktoken  # Token sayısını kontrol etmek için
import markdown  # Markdown'ı HTML'ye dönüştürmek için
from requests import request
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
# OpenAI istemcisi
client = OpenAI(api_key=settings.OPENAI_API_KEY)
from django.contrib.auth import login, logout


# Token ve dosya sınırları

MAX_TOKENS = 128000  # GPT-4o toplam token limiti
RESERVED_TOKENS = 15000  # Yanıtlar ve sistem mesajları için rezerv
MAX_FILE_SIZE = (MAX_TOKENS - RESERVED_TOKENS) * 4  # Dinamik hesaplama (456.000 karakter)





def upload_file(request):
    user = request.user
    if not user.is_active_member or user.analysis_credits <= 0:
        messages.error(request, "У вас больше нет прав на анализ. Пожалуйста, пополните ваш баланс.")
        return redirect('dashboard')

    """Загрузка и анализ файла."""
    if request.method == 'POST' and request.FILES.get('jupyter_file'):
        uploaded_file = request.FILES['jupyter_file']

        try:
            # Проверка размера файла
            content = uploaded_file.read().decode('utf-8')
            if len(content) > MAX_FILE_SIZE:
                return render(request, 'accounts/upload.html', {
                    'error': f"Файл слишком большой! Максимально допустимый размер: {MAX_FILE_SIZE} символов."
                })

            # Подсчёт количества токенов
            token_count = calculate_token_count(content)
            max_allowed_tokens = MAX_TOKENS - RESERVED_TOKENS

            if max_allowed_tokens < 0:
                raise ValueError(
                    "Максимальное количество токенов не может быть отрицательным. Проверьте значения MAX_TOKENS и RESERVED_TOKENS.")

            if token_count > max_allowed_tokens:
                return render(request, 'accounts/upload.html', {
                    'error': f"Файл слишком большой! Максимально допустимое количество токенов: {max_allowed_tokens}. Количество токенов в файле: {token_count}."
                })

            # Если всё в порядке, продолжить обработку файла
            # Здесь может быть добавлена логика анализа файла
            ...

        except UnicodeDecodeError:
            return render(request, 'accounts/upload.html', {
                'error': "Ошибка кодировки файла. Убедитесь, что файл закодирован в формате UTF-8."
            })

        except Exception as e:
            return render(request, 'accounts/upload.html', {
                'error': f"Произошла ошибка: {str(e)}"
            })

        try:
            # OpenAI API ile analiz yap
            completion = client.chat.completions.create(
                model="gpt-4o-2024-11-20",
                messages=[
                    {"role": "system", "content": """
                    You are an expert professor and a professional data analyst. Your task is to deeply analyze the content of the uploaded Jupyter Notebook and provide a detailed, structured feedback in Russian. Your analysis should focus on the following aspects:

                    1. **Libraries Used**: Identify which Python libraries are used in the notebook (e.g., pandas, numpy, matplotlib, seaborn, scikit-learn, etc.). Highlight any important libraries that are missing for:
                       - Data analysis
                       - Visualization
                       - Statistical testing
                       - Machine learning
                       Suggest libraries that the user should learn to enhance their analysis.

                    2. **Data Visualization**:
                       - Check which visualization libraries are used (e.g., matplotlib, seaborn, plotly).
                       - Evaluate the effectiveness of the visualizations.
                       - Provide recommendations for other visualization techniques and libraries that could improve the presentation of data.

                    3. **Statistical Testing**:
                       - Check whether statistical tests are performed (e.g., t-test, ANOVA, chi-square, etc.).
                       - Identify which tests are used and whether they are appropriate.
                       - Suggest statistical tests that should be added, if missing, and provide Python libraries that could assist.

                    4. **Machine Learning**:
                       - Check if machine learning is implemented in the notebook.
                       - Identify the algorithms and techniques used (e.g., regression, decision trees, clustering).
                       - Highlight missing machine learning algorithms or preprocessing steps and recommend libraries (e.g., scikit-learn, xgboost, keras).

                    5. **Workflow Analysis**:
                       - Assess whether the typical data analysis workflow is followed:
                         - Data loading
                         - Data cleaning
                         - Exploratory data analysis (EDA)
                         - Feature engineering
                         - Modeling
                         - Model evaluation
                       - Highlight which steps are missing or could be improved.
                       - Provide step-by-step suggestions for improvement.

                    6. **Code Quality**:
                       - Evaluate the quality of the code (e.g., readability, comments, structure).
                       - Suggest improvements for writing better, more efficient, and clean Python code.

                    7. **Final Recommendations**:
                       - Provide a comprehensive list of what the user should learn or improve.
                       - Include example Python libraries or specific functions that the user can study.

                    The goal is to provide a thorough, professor-level review of the notebook, pointing out the user’s strengths, weaknesses, and areas for improvement, with specific and actionable recommendations.Language=Russian,Limit response to 1500 tokens
                    """},
                    {"role": "user", "content": f"Analyze this file content: {content}"}
                ]
            )

            # API yanıtını al ve Markdown formatını HTML'ye çevir
            analysis_result = completion.choices[0].message.content.strip()
            html_result = markdown.markdown(analysis_result)  # Markdown'ı HTML'ye dönüştür
            user.analysis_credits -= 1
            if user.analysis_credits == 0:
                user.is_active_member = False
            user.save()  # Değişiklikleri kaydet
            # Şablona gönder
            return render(request, 'accounts/result.html', {'result': html_result})


        except Exception:

            # Hata durumunda kullanıcıya bilgi ver

            return render(request, 'accounts/upload.html', {

                'error': "Произошла ошибка во время обработки файла. Пожалуйста, попробуйте ещё раз через 1-2 минуты."

            })

    return render(request, 'accounts/upload.html', {
        'credits': user.analysis_credits,
        'is_active_member': user.is_active_member,
    })


def calculate_token_count(text):
    """Metindeki token sayısını hesaplar."""
    encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4o'nun kullandığı encoding
    tokens = encoding.encode(text)
    return len(tokens)


def parse_analysis_result(result):
    sections = {
        "Сильные стороны": [],
        "Слабые стороны": [],
        "Области для улучшения": []
    }

    current_section = None
    for line in result.split('\n'):
        if "Сильные стороны:" in line:
            current_section = "Сильные стороны"
        elif "Слабые стороны:" in line:
            current_section = "Слабые стороны"
        elif "Области для улучшения:" in line:
            current_section = "Области для улучшения"
        elif current_section and line.strip():
            sections[current_section].append(line.strip())

    # Konsolda bölümlerin içeriğini yazdır
    print("Сильные стороны:", sections["Сильные стороны"])
    print("Слабые стороны:", sections["Слабые стороны"])
    print("Области для улучшения:", sections["Области для улучшения"])
    return sections

