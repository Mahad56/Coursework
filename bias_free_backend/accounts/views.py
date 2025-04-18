from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages  
from django.core.exceptions import ValidationError
from .models import CustomUser 
import re
import pandas as pd
from django.contrib.auth.decorators import login_required
import sqlite3
from django.conf import settings
from posts.models import Post

#function for lgin view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('email')  
        password = request.POST.get('password')  
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            dummy_users = ["user1", "user2", "user3", "user4", "user5"] # list of the dummy accounts
            
            if user.username in dummy_users: #if the  user is a dummy account
                login(request, user)  #login
                return redirect('index')  #redirect to the main page
            else:
                messages.error(request, "This account is not a valid dummy account.")  
                return redirect('login')  # otherwise redirect back to the login page
        else:
            messages.error(request, "Invalid username or password.")  
            return redirect('login')  
    else:
        return render(request, 'accounts/login.html') 
#function to validate passwords      
def validate_password(password):
    if len(password) < 8:# minimum 8 charachters
        raise ValidationError("Password must be at least 8 characters long.")
    
    if not any(char.isdigit() for char in password):#minimum one number
        raise ValidationError("Password must contain at least one number.")
    
    if not any(char.isupper() for char in password):#must have at least one upper case letter
        raise ValidationError("Password must contain at least one uppercase letter.")
    
    special_characters = "!@#$%^&*()-_=+<>?"# must contaon one special charachter
    if not any(char in special_characters for char in password):
        raise ValidationError("Password must contain at least one special character.")

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        password = request.POST.get('password1')

        try:
            validate_password(password)

            if form.is_valid():
                user = form.save()  
                login(request, user)  
                return redirect('index')  

        except ValidationError as e:
            for error in e.messages:
                form.add_error('password1', error)  
                form.add_error('password2', error)

    else:
        form = UserCreationForm()

    return render(request, 'accounts/home.html', {'form': form})  

def home_view(request):
    return render(request, 'accounts/home.html')  

def index_view(request):
    return render(request, "index.html") 

def write_to_db(request):
    # Create a DataFrame
    new_posts_df = pd.DataFrame({
        'content': ['New Post 1', 'New Post 2'],
        'user_id': [1, 2]  # Assuming user IDs
    })

    # Connect to the SQLite database
    conn = sqlite3.connect(BASE_DIR / 'db.sqlite3')

    # Write the DataFrame to the 'posts_post' table 
    new_posts_df.to_sql('posts_post', conn, if_exists='append', index=False)

    # Close the connection
    conn.close()

    return render(request, 'posts/post_success.html')

    posts = Post.objects.all() 
    return render(request, 'posts/posts_list.html', {'posts': posts})

@login_required
def dashboard(request):
    return render(request, 'index.html', {'current_user': request.user})

def recommend_posts(request, user_id):
    # Fetch the posts based on sentiment analysis or the user's preferences
    user = User.objects.get(id=user_id)
    
    # Get the posts that match the user's dominant sentiment
    recommended_posts = Post.objects.filter(dominant_sentiment=user.dominant_sentiment)
    
    return render(request, 'opposing_views.html', {'user': user, 'recommended_posts': recommended_posts})

