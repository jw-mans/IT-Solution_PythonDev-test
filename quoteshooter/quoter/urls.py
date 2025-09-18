from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('top/<int:num_id>/', views.top_num_view, name='top'),
    path('top10/', views.top_10_view, name='top'),
    path('add/', views.add_new, name='add'),
    path('like/<int:quote_id>', views.like, name='like_quote'),
    path('dislike/<int:quote_id>', views.dislike, name='dislike_quote')
]

handler404 = views.page_not_found
