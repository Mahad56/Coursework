from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.post_list, name='posts_list'),
    path('raw-sql-query/', views.raw_sql_query, name='raw_sql_query'),
    path('create-post/', views.create_post, name='create_post'), 
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('remove-like/<int:post_id>/', views.remove_like_post, name='remove_like_post'),
    path('dislike/<int:post_id>/', views.dislike_post, name='dislike_post'),
    path('remove-dislike/<int:post_id>/', views.remove_dislike_post, name='remove_dislike_post'),
    path('comment/<int:post_id>/', views.create_comment, name='create_comment'),
    path('get-posts/', views.get_posts, name='get_posts'),
    path('get-sentiment-data/', views.get_sentiment_data, name='get_sentiment_data'),
    path('get-opposing-posts/<str:sentiment>/', views.get_opposing_sentiment_posts, name='get_opposing_sentiment_posts'),
    path('get-ordered-posts/<str:order_type>/', views.get_ordered_posts, name='get_ordered_posts'),
]