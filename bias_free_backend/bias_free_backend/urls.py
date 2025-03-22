"""
URL configuration for bias_free_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from accounts import views
from django.views.generic import TemplateView
from posts import views as post_views  # Add this import for post_views
from django.http import HttpResponse


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('posts/', include('posts.urls')),  
    path('', views.signup_view, name='home'), 
    path('create/', post_views.create_post, name='create_post'), 
    path('favicon.ico', lambda x: HttpResponse(status=204)),
]