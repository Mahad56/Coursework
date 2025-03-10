from django.urls import path
from . import views  

urlpatterns = [
    path('login/', views.login_view, name='login'),  
    path('home/', views.home_view, name='home'),  
    path('index/', views.index_view, name='index'),  
]
