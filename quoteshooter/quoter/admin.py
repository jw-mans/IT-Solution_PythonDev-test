from django.contrib import admin
from .models import Source, Quote


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("id", "data")
    search_fields = ("data",)


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("id", "text_short", "source", "weight", "views_cnt", "likes", "dislikes", "creation_time")
    list_filter = ("source", "creation_time")
    search_fields = ("text", "source__data")
    ordering = ("-creation_time",)

    def text_short(self, obj):
        return (obj.text[:50] + "...") if len(obj.text) > 50 else obj.text
    text_short.short_description = "Текст"
