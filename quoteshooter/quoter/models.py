from django.db import models
from django.db.models import F, Sum
from django.core.exceptions import ValidationError

class Source(models.Model):
    data = models.CharField(max_length=511, unique=True)

    def __str__(self):
        return self.data
    
    @classmethod
    def default(cls):
        return cls.objects.get_or_create(data="Неизвестно")[0]
    
class Quote(models.Model):
    text = models.TextField(default="")
    source = models.ForeignKey(Source,
        on_delete=models.PROTECT,
        related_name='quotes',
        default=Source.default
    )
    weight = models.PositiveIntegerField(default=0)
    views_cnt = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    creation_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['text', 'source'],
                name='unique_text_per_source'
            ),
            models.CheckConstraint(
                check=~models.Q(text=""),
                name='quote_text_not_empty'
            ),
        ]

    def clean(self):
        if self.pk is None:
            existing = Quote.objects.filter(source=self.source).count()
            if existing >= 3:
                raise ValidationError(
                    f"Source already has {existing} quotes, no more than 3!"
                )
    
    @classmethod
    def weighted_random(cls):
        """
        Возвращает один экземпляр Quote с учётом веса (W).
        Реализация на стороне Python — приемлема для небольших пулов.
        Для огромных данных можно сделать выборку в БД.

        Пусть есть три цитаты:
        1) A: W(A)=2
        2) B: W(B)=5
        3) C: W(C)=8

        Тогда:
        quotes = [A, B, C]
        total_weight = W(A) + W(B) + W(C) = 15

        Выбираем произвольное число __random_point \in [0; total_weight].

        __cumul - накопленный вес:

             ^ _cumul
             |        
        15 > |    o---
             |       
        7  > | o---  
             |       
        2  > +--     
             o-+--+--+ W
               ^  ^  ^
               A  B  C
        
        И дальше возвращается цитата соответствующая неравенству:
        __random_point <= __cumul

        """
        EMPTY_QUOTES_LIST_WEIGHT = -1
        import random

        __quotes = cls.objects.all()

        total_weight = __quotes.aggregate(
            total=Sum('weight')
        )['total'] or EMPTY_QUOTES_LIST_WEIGHT # if no quotes in db

        if total_weight == EMPTY_QUOTES_LIST_WEIGHT: # if no quotes in db
            return None 
        
        __random_cumul_weight = random.uniform(0, total_weight)
        __cumul = 0.0
        for _q in __quotes:
            __cumul += _q.weight
            if __random_cumul_weight <= __cumul:
                return _q
            
        return __quotes.last()
    
    def __atomar(self, **kwargs):
        """
        Атомарно изменяет значение какого-либо поля

        Args:
            **kwargs: Any - выражение для изменения
        """
        Quote.objects.filter(pk=self.pk).update(**kwargs)

    def increase_views(self):
        self.__atomar(views_cnt=F('views_cnt') + 1)
    
    def like(self):
        self.__atomar(likes=F('likes') + 1)

    def dislike(self):
        self.__atomar(dislikes=F('dislikes') + 1)

    def save(self, *args, **kwargs):
        self.full_clean()
        
        import random
        if self.pk is None and self.weight == 0:
            self.weight = random.randint(1, 100)
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f'"{self.text[:50]}...": {self.source}'