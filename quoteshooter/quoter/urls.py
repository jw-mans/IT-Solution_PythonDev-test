from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('top/<int:num_id>/', views.top_quotes_view, {'by': 'views'}, name='top'),
    path('top10/', views.top_10_view, name='top10'),
    path('top/likes/<int:num_id>/', views.top_quotes_view, {'by': 'likes'}, name='top_likes'),
    path('top10/likes/', views.top_10_like, name='top10_likes'),
    path('add/', views.add_new, name='add'),
    path('like/<int:quote_id>', views.like, name='like_quote'),
    path('dislike/<int:quote_id>', views.dislike, name='dislike_quote'),
    path('api/quote/random/', views.api_random_quote, name='api_random_quote')
]

handler404 = views.page_not_found
