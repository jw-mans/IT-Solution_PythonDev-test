from django import forms
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from .models import Quote, Source
from core.logger import logger

class QuoteForm(forms.ModelForm):
    """
    Форма для добавления новой цитаты.

    Поля формы:
        author (str): Автор цитаты (необязательное поле).
        name (str): Название цитаты/произведения (необязательное поле).
        text (str): Текст цитаты (обязательное поле).
    """
    author = forms.CharField(
        max_length=255,
        required=False,
        label='Автор'
    )
    name = forms.CharField(
        max_length=255,
        required=False,
        label='Название'
    )
    text = forms.CharField(
        widget=forms.Textarea,
        label='Текст'
    )

    class Meta:
        model = Quote
        fields = ['author', 'name', 'text']

    def clean_text(self):
        """
        Просто очищаем текст (убираем лишние пробелы).
        """
        _text = self.cleaned_data.get('text', '').strip()
        if not _text:
            raise forms.ValidationError('Поле "Текст" не может быть пустым.')
        return _text

    def clean(self):
        cleaned = super().clean()

        author = (cleaned.get('author') or '').strip()
        name = (cleaned.get('name') or '').strip()
        text = (cleaned.get('text') or '').strip()

        src_text = f'{author} "{name}"' if author and name else name or author or "Неизвестно"

        if text:
            dup = Quote.objects.filter(
                text__iexact=text,
                source__data__iexact=src_text
            ).exists()
            if dup:
                self.add_error('text', 'Такая цитата уже существует для этого источника.')

        src_qs = Source.objects.filter(data__iexact=src_text)
        if src_qs.exists():
            src_obj = src_qs.first()
            if (src_obj.data or '').strip().lower() != 'неизвестно':
                count = Quote.objects.filter(source=src_obj).count()
                if count >= 3:
                    self.add_error(None, f'У источника "{src_text}" уже {count} цитаты. Нельзя добавить больше 3.')

        cleaned['author'] = author
        cleaned['name'] = name
        cleaned['text'] = text
        cleaned['src_text'] = src_text

        return cleaned



    def save(self, commit=True):
        """
        Сохраняет объект Quote.
        Когда форма уже валидна, создаём/получаем Source и сохраняем Quote.
        """
        quote = super().save(commit=False)

        author = self.cleaned_data.get('author', '')
        name = self.cleaned_data.get('name', '')

        try:
            quote.source = Quote.make_source(author, name)
        except Exception as e:
            logger.error(f'Ошибка при создании источника для цитаты: {e}')
            raise ValidationError('Ошибка при создании/получении источника.')

        if commit:
            quote.save()

        logger.info(f'Цитата успешно сохранена через форму: {quote.id}')
        return quote
