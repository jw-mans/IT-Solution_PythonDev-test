from django import forms
from .models import Quote, Source

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
        Проверка уникальности текста цитаты без учёта регистра.
        
        Raises:
            forms.ValidationError: если цитата уже существует в базе.
        
        Returns:
            str: очищенный текст цитаты.
        """
        _text = self.cleaned_data['text'].strip()
        if Quote.objects.filter(text__iexact=_text).exists():
            raise forms.ValidationError('Цитата уже существует.')
        return _text
        
    def save(self, commit=True):
        """
        Сохраняет объект Quote.

        Логика:
            1. Формируем поле source на основе введённых author и name.
               Возможные варианты:
                 - <Автор> "<Название>"
                 - "<Название>"
                 - <Автор>
                 - "Неизвестно" (если пусто)
            2. Создаём или получаем объект Source.
            3. Присваиваем source объекту Quote.
            4. Сохраняем Quote (если commit=True).

        Args:
            commit (bool): если True, сразу сохраняем объект в БД.

        Returns:
            Quote: сохранённый объект цитаты.
        """
        quote = super().save(commit=False)

        author = self.cleaned_data.get('author', '').strip()
        name = self.cleaned_data.get('name', '').strip()

        # Формируем текст источника
        src_text = f'{author} "{name}"' if author and name \
            else name or author or "Неизвестно"
        src_obj = Source.objects.get_or_create(data=src_text)[0]
        quote.source = src_obj
                
        if commit:
            quote.save()

        return quote
