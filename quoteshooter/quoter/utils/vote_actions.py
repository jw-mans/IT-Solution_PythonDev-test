from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from ..models import Quote

LIKE_ = "like"
DISLIKE_ = "dislike"

def __rate_quote(request, quote_id, action):
    """
    Универсальная функция для обработки лайков и дизлайков цитаты.

    Логика:
        - Если пользователь уже голосовал так же, снимается голос.
        - Если пользователь голосует противоположно, старый голос убирается, новый добавляется.
        - Ограничение: за одну сессию можно изменить количество лайков/дизлайков для каждой цитаты только один раз.

    Args:
        request (HttpRequest): объект запроса.
        quote_id (int): ID цитаты.
        action (str): тип действия - "like" или "dislike".

    Returns:
        JsonResponse: словарь с обновленными счетчиками {'likes': int, 'dislikes': int}.
    """
    quote = get_object_or_404(Quote, pk=quote_id)
    session_key = f'quote_vote_{quote_id}'
    prev_vote = request.session.get(session_key)

    if prev_vote == action:
        if action == "like":
            quote.likes = max(0, quote.likes - 1)
        else:
            quote.dislikes = max(0, quote.dislikes - 1)
        request.session.pop(session_key)
    else:
        opposite = "dislike" if action == "like" else "like"
        if prev_vote == opposite:
            if opposite == "like":
                quote.likes = max(0, quote.likes - 1)
            else:
                quote.dislikes = max(0, quote.dislikes - 1)
        if action == "like":
            quote.likes += 1
        else:
            quote.dislikes += 1
        request.session[session_key] = action

    quote.save(update_fields=['likes', 'dislikes'])
    quote.refresh_from_db(fields=["likes", "dislikes"])
    return JsonResponse({"likes": quote.likes, "dislikes": quote.dislikes})

def like_quote(request, quote_id):
    """
    Обработчик лайка цитаты.

    Args:
        request (HttpRequest): объект запроса.
        quote_id (int): ID цитаты.

    Returns:
        JsonResponse: обновленные значения likes и dislikes.
    """
    return __rate_quote(request, quote_id, LIKE_)

def dislike_quote(request, quote_id):
    """
    Обработчик дизлайка цитаты.

    Args:
        request (HttpRequest): объект запроса.
        quote_id (int): ID цитаты.

    Returns:
        JsonResponse: обновленные значения likes и dislikes.
    """
    return __rate_quote(request, quote_id, DISLIKE_)
