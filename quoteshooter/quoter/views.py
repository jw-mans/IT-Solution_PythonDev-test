from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Quote
from .forms import QuoteForm
from .utils.vote_actions import like_quote, dislike_quote

def index(request):
    """
    Главная страница.

    Логика:
        1. Выбирает случайную цитату с учетом веса.
        2. Увеличивает счетчик просмотров.
        3. Отображает шаблон 'quoter/index.html' с контекстом {'quote': quote}.
    """
    quote = Quote.weighted_random()
    if quote:
        quote.increase_views()
    return render(request, 'quoter/index.html', {'quote': quote})

def top_num_view(request, num_id):
    """
    Отображение топ-N цитат по просмотрам.

    Args:
        request (HttpRequest): объект запроса.
        num_id (int): количество цитат для отображения.

    Returns:
        HttpResponse: рендер шаблона 'quoter/top.html' с топ-цитатами.
    """
    quotes = Quote.objects.order_by('-views_cnt')[:num_id]
    return render(request, 'quoter/top.html', {
        'quotes': quotes,
        'num_id': num_id
    })

def top_10_view(request):
    """
    Перенаправление на топ-10 цитат.

    Логика:
        Перенаправляет на URL 'top' с аргументом 10.
    """
    uri = reverse('top', args=(10,))
    return redirect(uri, permanent=True)

def page_not_found(request, exception):
    """
    Обработчик 404 ошибки.

    Args:
        request (HttpRequest): объект запроса.
        exception (Exception): исключение, вызвавшее 404.

    Returns:
        HttpResponse: рендер шаблона 'quoter/404.html'.
    """
    return render(request, 'quoter/404.html')

def add_new(request):
    """
    Добавление новой цитаты через форму.

    Логика:
        1. Если метод POST:
            - Создает форму с POST-данными.
            - Если форма валидна, сохраняет Quote и редиректит на главную.
        2. Если метод GET:
            - Создает пустую форму.
        3. Рендерит шаблон 'quoter/add.html' с формой.

    Returns:
        HttpResponse: рендер шаблона с формой.
    """
    if request.method == "POST":
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = QuoteForm()

    return render(request, 'quoter/add.html', {'form': form})

@require_POST
def like(request, quote_id):
    """
    Обработчик лайка цитаты.

    Args:
        request (HttpRequest): объект запроса.
        quote_id (int): ID цитаты.

    Returns:
        JsonResponse: обновленные значения likes и dislikes.
    """
    return like_quote(request, quote_id)

@require_POST
def dislike(request, quote_id):
    """
    Обработчик дизлайка цитаты.

    Args:
        request (HttpRequest): объект запроса.
        quote_id (int): ID цитаты.

    Returns:
        JsonResponse: обновленные значения likes и dislikes.
    """
    return dislike_quote(request, quote_id)
