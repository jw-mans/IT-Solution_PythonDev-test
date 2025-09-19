from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.http import JsonResponse

import json

from .models import Quote
from .forms import QuoteForm
from .utils.vote_actions import like_quote, dislike_quote

from core.logger import logger

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
        logger.info(f'Отображена цитата на главной: {quote.id}')
    return render(request, 'quoter/index.html', {'quote': quote})

def api_random_quote(request):
    """
    Возвращает JSON случайной цитаты.
    """
    quote = Quote.weighted_random()
    if quote:
        quote.increase_views()
        data = {
            'quote': {
                'id': quote.id,
                'text': quote.text,
                'source': str(quote.source),
                'views_cnt': quote.views_cnt,
                'likes': quote.likes,
                'dislikes': quote.dislikes,
                'weight': float(quote.weight)
            }
        }
        logger.info(f'API вернул цитату: {quote.id}')
    else:
        data = {'quote': None}
        logger.info('API вернул пустую цитату.')
    return JsonResponse(data)

def top_quotes_view(request, num_id, by='views'):
    """
    Отображает топ-N цитат по просмотрам или лайкам.

    Args:
        request (HttpRequest)
        num_id (int): количество цитат
        by (str): 'views' или 'likes'

    Returns:
        HttpResponse: рендер шаблона 'quoter/top.html'
    """
    if by == 'views':
        field = 'views_cnt'
        icon = '🔥'
        title_text = f'Топ {num_id} цитат по просмотрам'
    else:
        field = 'likes'
        icon = '❤️'
        title_text = f'Топ {num_id} цитат по лайкам'

    quotes = Quote.objects.order_by(f'-{field}')[:num_id]
    logger.info(f'Отображен топ-{num_id} цитат по {field}')

    return render(request, 'quoter/top.html', {
        'quotes': quotes,
        'num_id': num_id,
        'title_icon': icon,
        'title_text': title_text
    })

def top_10_view(request):
    logger.info('Перенаправление на топ-10 по просмотрам')
    return redirect(reverse('top', args=(10,)), permanent=True)

def top_10_like(request):
    logger.info('Перенаправление на топ-10 по лайкам')
    return redirect(reverse('top_likes', args=(10,)), permanent=True)

def page_not_found(request, exception):
    """
    Обработчик 404 ошибки.

    Args:
         request (HttpRequest): объект запроса.
         exception (Exception): исключение, вызвавшее 404.

    Returns:
        HttpResponse: рендер шаблона 'quoter/404.html'.
    """
    logger.warning(f'404 ошибка: {request.path}')
    return render(request, 'quoter/404.html')

def add_new(request):
    """
    Добавление новой цитаты через форму:

        1. Если метод POST:
            - Создает форму с POST-данными.
            - Если форма валидна, сохраняет Quote и редиректит на главную.
        2. Если метод GET:
            - Создает пустую форму.
        3. Рендерит шаблон 'quoter/add.html' с формой.
    """
    if request.method == "POST":
        form = QuoteForm(request.POST)
        if form.is_valid():

            from django.db import IntegrityError
            from django.core.exceptions import ValidationError

            try:
                form.save()

            except IntegrityError as e:
                logger.warning(f'IntegrityError при сохранении цитаты: {e}')
                form.add_error(None, 'Такая цитата уже существует в базе данных.')

            except ValidationError as e:
                msgs = getattr(e, 'messages', None) or [str(e)]
                for m in msgs:
                    form.add_error(None, m)
                logger.warning(f'ValidationError при сохранении цитаты: {e}')

            except Exception as e:

                logger.exception(f'Непредвиденная ошибка при сохранении цитаты: {e}')
                form.add_error(None, 'Непредвиденная ошибка при сохранении цитаты. Повторите попытку позже.')

            else:
                logger.info(f'Добавлена новая цитата.')
                return redirect('home')
        else:
            logger.warning('Ошибка валидации формы добавления цитаты')
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
    logger.info(f'Лайк для цитаты {quote_id}')
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
    logger.info(f'Дизлайк для цитаты {quote_id}')
    return dislike_quote(request, quote_id)

@require_POST
def update_weight(request, quote_id):
    try:
        data = json.loads(request.body)
        new_weight = float(data.get("weight", 0))
        if not (0 <= new_weight <= 100):
            return JsonResponse({"success": False, "error": "Вес должен быть от 0 до 100."})

        quote = Quote.objects.get(pk=quote_id)
        quote.weight = new_weight
        quote.save(update_fields=["weight"])
        logger.info(f"Вес цитаты {quote.id} изменён на {new_weight:.2f}")
        return JsonResponse({"success": True, "weight": new_weight})
    except Quote.DoesNotExist:
        return JsonResponse({"success": False, "error": "Цитата не найдена."})
    except Exception as e:
        logger.exception(f"Ошибка при изменении веса: {e}")
        return JsonResponse({"success": False, "error": "Ошибка на сервере."})