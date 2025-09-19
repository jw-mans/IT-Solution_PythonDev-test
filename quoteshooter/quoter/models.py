from django.db import models
from django.db.models import F, Sum
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from core.logger import logger

class Source(models.Model):
    """Модель источника цитаты."""
    data = models.CharField(max_length=511, unique=True)

    def __str__(self):
        return self.data
    
    @classmethod
    def default(cls):
        """
        Возвращает объект Source по умолчанию.
        Если его нет в базе, создаёт новый с data="Неизвестно".
        """
        obj, create_flag = cls.objects.get_or_create(data="Неизвестно")
        if create_flag:
            logger.info(f'Создан новый источник по умолчанию: {obj}')
        return obj
    
class Quote(models.Model):
    """Модель цитаты.

    Args:
        text (str): Текст цитаты.
        source (ForeignKey[Source]): Источник цитаты.
        weight (float): Вес для случайного выбора.
        views_cnt (int): Количество просмотров.
        likes (int): Количество лайков.
        dislikes (int): Количество дизлайков.
        creation_time (datetime): Время создания.
    """
    text = models.TextField(default="")
    source = models.ForeignKey(Source,
        on_delete=models.PROTECT,
        related_name='quotes',
        default=Source.default
    )
    weight = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0.0), 
            MaxValueValidator(100.0),
        ], # для админки и обработки ошибок
        help_text="Вес цитаты для функции weighted_random (0-100)"
    )
    views_cnt = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    creation_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # текст цитаты должен быть уникален на источник
            # (т. о. допускается использование одного текста на разные источники)
            models.UniqueConstraint(
                fields=['text', 'source'],
                name='unique_text_per_source'
            ),
            # текст цитаты не должен быть пустым
            models.CheckConstraint(
                check=~models.Q(text=""),
                name='quote_text_not_empty'
            ),
            # для ручного добавления в БД
            models.CheckConstraint(
                check=models.Q(weight__gte=0.0) & \
                      models.Q(weight__lte=100.0),
                name='weight_1_and_100_bounds'
            )
        ]

    def clean(self):
        """
        Проверка перед сохранением.
        Ограничение: не более 3 цитат на один источник,
        исключение: для источника "Неизвестно" ограничение НЕ применяется.
        """
        if self.pk is None:
            src_data = (getattr(self.source, 'data', '') or '').strip().lower()
            if src_data == 'неизвестно':
                return

            existing = Quote.objects.filter(source=self.source).count()
            if existing >= 3:
                logger.warning(f'Невозможно создать цитату: источник {self.source} уже имеет {existing} цитаты.')
                raise ValidationError(
                    f"Source already has {existing} quotes, no more than 3!"
                )
    
    @classmethod
    def weighted_random(cls):
        """
        Возвращает один объект Quote случайно с учетом веса.

        Algorithm:
            1. Вычисляем суммарный вес всех цитат.
            2. Выбираем случайное число в диапазоне [0, total_weight].
            3. Проходим по цитатам и суммируем их веса.
            4. Возвращаем первую цитату, у которой накопленный вес >= random_point.
        
        Returns:
            Quote | None: Случайная цитата или None, если база пуста.
        """
        
        #Реализация на стороне Python — приемлема для небольших пулов.
        #Для огромных данных можно сделать выборку в БД.

        #Пусть есть три цитаты:
        #1) A: W(A)=2
        #2) B: W(B)=5
        #3) C: W(C)=8
        #W(<цитата>) - вес цитаты

        #Тогда:
        #quotes = [A, B, C]
        #total_weight = W(A) + W(B) + W(C) = 15

        #Выбираем произвольное число __random_point \in [0; total_weight].

        #__cumul - накопленный вес:

        #     ^ _cumul
        #     |        
        #15 > |    o---
        #     |       
        #7  > | o---  
        #     |       
        #2  > +--     
        #     o-+--+--+ W
        #       ^  ^  ^
        #       A  B  C
        
        #И дальше возвращается цитата соответствующая неравенству:
        #__random_point <= __cumul

        
        EMPTY_QUOTES_LIST_WEIGHT = -1.0
        import random

        __quotes = cls.objects.all()

        total_weight = __quotes.aggregate(
            total=Sum('weight')
        )['total'] or EMPTY_QUOTES_LIST_WEIGHT # если цитат нет

        if total_weight == EMPTY_QUOTES_LIST_WEIGHT:
            logger.info('Нет цитат для случайного выбора.')
            return None 
        
        __random_cumul_weight = random.uniform(0.0, total_weight)
        __cumul = 0.0
        for _q in __quotes:
            __cumul += _q.weight
            if __random_cumul_weight <= __cumul:
                logger.info(f'Выбрана случайная цитата: {_q.id}')
                return _q
            
        logger.info(f'Выбрана последняя цитата: {__quotes.last().id}')
        return __quotes.last()
    
    def __atomar(self, **kwargs):
        """
        Атомарно изменяет значение какого-либо поля

        Args:
            **kwargs: Any - выражение для изменения
        """
        Quote.objects.filter(pk=self.pk).update(**kwargs)

    def increase_views(self):
        """
        Увеличивает счетчик просмотров на 1 атомарно.
        """
        self.__atomar(views_cnt=F('views_cnt') + 1)
        logger.info(f'Увеличен счетчик просмотров цитаты {self.id}: {self.views_cnt + 1}')

    def save(self, *args, **kwargs):
        """
        Переопределенный метод save.
        1. Проверяет данные через full_clean().
        2. Если вес не указан при создании, присваивает случайное значение 0-100.
        """

        self.full_clean()
        
        import random
        if self.pk is None and self.weight == 0.0:
            self.weight = random.uniform(0.0, 100.0)
            logger.info(f'Присвоен случайный вес цитате: {self.weight:.2f}')
            
        super().save(*args, **kwargs)
        logger.info(f'Сохранена цитата {self.id}: "{self.text[:30]}..."')

    def __str__(self):
        """
        Строковое представление объекта:
        первые 50 символов текста + источник.
        """
        return f'"{self.text[:50]}...": {self.source}'
    
    @staticmethod
    def make_source(author, name):
        """
        Формирует объект Source по автору и названию произведения.

        Правила:
            - <Автор> "<Название>"
            - "<Название>"
            - <Автор>
            - "Неизвестно" (если оба поля пустые)

        Args:
            author (str): Автор цитаты
            str (str): Название источника
        """
        author, name = author.strip(), name.strip()
        src_text = f'{author} "{name}"' if author and name else name or author or "Неизвестно"
        obj, create_flag = Source.objects.get_or_create(data=src_text)
        if create_flag:
            logger.info(f'Создан источник: {obj}')
        return obj