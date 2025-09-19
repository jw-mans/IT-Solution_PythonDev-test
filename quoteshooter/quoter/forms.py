from django import forms
from django.core.exceptions import ValidationError
from .models import Quote, Source
from core.logger import logger
import random

class QuoteForm(forms.ModelForm):
    author = forms.CharField(max_length=255, required=False, label='Автор')
    name = forms.CharField(max_length=255, required=False, label='Название')
    text = forms.CharField(widget=forms.Textarea, label='Текст')
    weight = forms.FloatField(
        label='Вес (0-100)',
        required=False,
        min_value=0.0,
        max_value=100.0,
        help_text='Чем выше вес, тем больше шанс цитаты появиться на главной'
    )

    class Meta:
        model = Quote
        fields = ['author', 'name', 'text', 'weight']

    def clean_text(self):
        _text = self.cleaned_data.get('text', '').strip()
        if not _text:
            raise forms.ValidationError('Поле "Текст" не может быть пустым.')
        return _text

    def clean_weight(self):
        w = self.cleaned_data.get('weight')
        if w in (None, ''):
            w = random.uniform(0.0, 100.0)
            logger.info(f'Присвоен случайный вес через форму: {w:.2f}')
        return float(w)

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
        quote = super().save(commit=False)

        author = self.cleaned_data.get('author', '')
        name = self.cleaned_data.get('name', '')
        quote.weight = self.cleaned_data.get('weight')

        try:
            quote.source = Quote.make_source(author, name)
        except Exception as e:
            logger.error(f'Ошибка при создании источника для цитаты: {e}')
            raise ValidationError('Ошибка при создании/получении источника.')

        if commit:
            quote.save()

        logger.info(f'Цитата успешно сохранена через форму: {quote.id}')
        return quote
