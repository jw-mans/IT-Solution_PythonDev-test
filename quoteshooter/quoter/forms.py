from django import forms
from .models import Quote, Source

class QuoteForm(forms.ModelForm):
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
        Проверка уникальности текста цитаты (без учета регистра).
        Если такая цитата уже есть, выбрасываем ValidationError.
        """
        _text = self.cleaned_data['text'].strip()
        if Quote.objects.filter(text__iexact=_text).exists():
            raise forms.ValidationError('Цитата уже существует.')
        return _text
        
    def save(self, commit=True):
        """
        Сохраняем объект Quote, формируем поле source на основе 
        введенных author и name, проверяем на условие количества.
        """
        quote = super().save(commit=False)

        author = self.cleaned_data.get('author', '').strip()
        name = self.cleaned_data.get('name', '').strip()

        # Заполняем поле source форматированной из имени автора и названия цитаты.
        #
        # Доступно:
        # 1) <Автор> "<Название>";
        # 2) "<Название>";
        # 3) <Автор>;
        # 4) Неизвестно

        src_text = f'{author} "{name}"' if author and name \
            else name or author or "Неизвестно"
        src_obj = Source.objects.get_or_create(data=src_text)[0]
        quote.source = src_obj
                
        if commit:
            quote.save()

        return quote