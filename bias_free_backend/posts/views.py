from django.db.models import F
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from .models import Post, Comment
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import sqlite3
import pandas as pd
from django.contrib import messages  
import json
from django.http import JsonResponse
from django.db.models import Prefetch
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from accounts.models import CustomUser
nltk.download('vader_lexicon')

def post_list(request, user_id=None):
    if user_id:
        user = get_object_or_404(CustomUser, id=user_id)
        posts = Post.objects.filter(user=user).prefetch_related('comments', 'liked_by', 'disliked_by')
    else:
        posts = Post.objects.prefetch_related('comments', 'liked_by', 'disliked_by').all()
    
    # Calculate sentiment for each user
    users_data = []

    for user in CustomUser.objects.all():
        user_posts = Post.objects.filter(user=user)
        
        total_posts = user_posts.count()
        positive_count = user_posts.filter(sentiment_label='Positive').count()
        negative_count = user_posts.filter(sentiment_label='Negative').count()
        neutral_count = user_posts.filter(sentiment_label='Neutral').count()

        #calculate the prefered sentiment percentages
        if total_posts > 0:
            positive_percentage = (positive_count / total_posts) * 100
            negative_percentage = (negative_count / total_posts) * 100
            neutral_percentage = (neutral_count / total_posts) * 100
        else:
            positive_percentage = negative_percentage = neutral_percentage = 0

        # Add the user sentiment data to the list
        users_data.append({
            'user': user.username,
            'positive_percentage': positive_percentage,
            'negative_percentage': negative_percentage,
            'neutral_percentage': neutral_percentage,
        })
    #post data
    posts_data = []
    for post in posts:
        post_data = {
            'id': post.id,
            'uuid': post.uuid,
            'content': post.content,
            'user': post.user.username,
            'created_at': post.created_at.isoformat(),
            'likes': post.liked_by.count(),
            'dislikes': post.disliked_by.count(),
            'sentiments': post.sentiment_label,
            'comments': [
                {
                    'id': comment.id,
                    'content': comment.content,
                    'user': comment.user.username,
                    'created_at': comment.created_at.isoformat(),
                }
                for comment in post.comments.all() #fetch al the comments for the post
            ],
        }
        posts_data.append(post_data)

    return render(request, 'posts/posts_list.html', {
        'posts': posts_data,
        'user': user if user_id else None,  # Include the user
        'user_sentiments': users_data,  # Include the calculated sentiment data
    })

@csrf_exempt
def create_post(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            post_content = data.get('content', '')

            if post_content:
                # Initialize SentimentIntensityAnalyzer
                sid = SentimentIntensityAnalyzer()
                sentiment = sid.polarity_scores(post_content)
                sentiment_score = sentiment['compound']  # Get the compound sentiment score

                # Classify sentiment into Positive, Negative, or Neutral, https://akladyous.medium.com/sentiment-analysis-using-vader-c56bcffe6f24#:~:text=Notice%20that%20the,compound%20score%3C%3D%2D0.05
                if sentiment_score > 0.1:
                    sentiment_label = 'Positive'
                elif sentiment_score < -0.1:
                    sentiment_label = 'Negative'
                else:
                    sentiment_label = 'Neutral'

                # Create and save the new post
                new_post = Post(content=post_content, user=request.user, sentiment_label=sentiment_label, sentiment_score=sentiment_score)
                new_post.save()

                # Return success response with the created post data
                return JsonResponse({
                    'message': 'Post created successfully',
                    'id': new_post.id,
                    'uuid': new_post.uuid,
                    'content': new_post.content,
                    'user': request.user.username,
                    'likes': new_post.liked_by.count(),
                    'dislikes': new_post.disliked_by.count(),
                    'sentiments': new_post.sentiment_label, 
                    'created_at': new_post.created_at.isoformat(),
                }, status=201)
            else:
                return JsonResponse({'error': 'Post content is empty'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
@login_required
def create_comment(request, post_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content')

            if not content:
                return JsonResponse({'error': 'Comment content is required.'}, status=400)

            post = Post.objects.get(id=post_id)

            # Create and save the comment
            comment = Comment.objects.create(
                content=content,
                post=post,
                user=request.user
            )

            return JsonResponse({
                'comment_id': comment.id,
                'user': comment.user.username,
                'content': comment.content,
            }, status=201)

        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def like_post(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)

        #
        if request.user not in post.liked_by.all():
            post.liked_by.add(request.user)  
            post.save()

        return JsonResponse({'message': 'Post liked successfully', 'likes': post.liked_by.count()})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def dislike_post(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)

        # Check if the user already disliked the post
        if request.user in post.disliked_by.all():
            post.disliked_by.remove(request.user)  # Remove the dislike
            user_action = 'none'
        else:
            post.disliked_by.add(request.user)  # Add the dislike
            post.liked_by.remove(request.user)  # Remove like if they have liked already
            user_action = 'dislike'

        post.save()
        return JsonResponse({
            'message': 'Post dislike status updated',
            'likes': post.liked_by.count(),
            'dislikes': post.disliked_by.count(),
            'user_action': user_action
        })

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def get_posts(request):
    """
    This view retrieves all posts and their associated comments, 
    and returns them as a JSON response.
    """
    # Prefetch comments related to posts to reduce database queries
    posts = Post.objects.prefetch_related(
        Prefetch('comments', queryset=Comment.objects.all())
    ).order_by('-created_at')  # Adjust to your model

    posts_data = []

    # Iterate through the posts and fetch associated comments
    for post in posts:
        post_data = {
            'id': post.id,
            'uuid': post.uuid,
            'content': post.content,
            'user': post.user.username,
            'created_at': post.created_at.isoformat(),
            'likes': post.liked_by.count(),
            'dislikes': post.disliked_by.count(),
            'comments': [
                {
                    'id': comment.id,
                    'content': comment.content,
                    'user': comment.user.username,
                    'created_at': comment.created_at.isoformat(),
                }
                for comment in post.comments.all()
            ]
        }
        posts_data.append(post_data)

    return JsonResponse({'posts': posts_data})

def raw_sql_query(request):
    
    # Connect to the SQLite database
    db_path = settings.BASE_DIR / "db.sqlite3"  # Use BASE_DIR to refer to the DB file

    # Execute raw SQL query
    conn = sqlite3.connect(db_path)
    query = """
    SELECT p.id AS post_id, u.username, p.content, p.created_at 
    FROM posts_post p 
    JOIN accounts_customuser u ON p.user_id = u.id
    """
    df = pd.read_sql_query(query, conn)


    # Convert DataFrame to a list of dictionaries
    posts = df.to_dict(orient='records')

    # Close the connection
    conn.close()

    # Render the template with the posts data
    return render(request, 'posts/posts_list.html', {'posts': posts})


@csrf_exempt
@login_required
def remove_like_post(request, post_id):
    """
    Toggles the like status for a post.
    If the user has already liked the post, the like is removed.
    Otherwise, a like is added.
    """
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)

        if request.user in post.liked_by.all():
            # If the user has already liked, remove the like
            post.liked_by.remove(request.user)
            user_action = 'none'  
        else:
            # If the user hasn't liked, add the like and remove any existing dislike
            post.liked_by.add(request.user)
            post.disliked_by.remove(request.user)  # Remove the dislike if it exists
            user_action = 'like'

        post.save()

        # Return updated counts
        return JsonResponse({
            'message': 'Like status updated.',
            'likes': post.liked_by.count(),
            'dislikes': post.disliked_by.count(),
            'user_action': user_action  
        })

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
@login_required
def remove_dislike_post(request, post_id):
    """
    Toggles the dislike status for a post.
    If the user has already disliked the post, the dislike is removed.
    Otherwise, a dislike is added.
    """
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)

        if request.user in post.disliked_by.all():
            # If the user has already disliked, remove the dislike
            post.disliked_by.remove(request.user)
            user_action = 'none'  
        else:
            # If the user hasn't disliked, add the dislike and remove any existing like
            post.disliked_by.add(request.user)
            post.liked_by.remove(request.user)  # Remove the like if it exists
            user_action = 'dislike'

        post.save()

        # Return updated counts
        return JsonResponse({
            'message': 'Dislike status updated.',
            'likes': post.liked_by.count(),
            'dislikes': post.disliked_by.count(),
            'user_action': user_action
        })

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

# Function that returns sentiment data
def get_sentiment_data(request):
    users_data = []  # List to store the sentiment data for all users

    # Iterate through all users
    for user in CustomUser.objects.all():
        # Get posts for each user
        user_posts = Post.objects.filter(user=user)
        
        total_posts = user_posts.count()
        positive_count = user_posts.filter(sentiment_label='Positive').count()
        negative_count = user_posts.filter(sentiment_label='Negative').count()
        neutral_count = user_posts.filter(sentiment_label='Neutral').count()

        # Calculate percentages for each sentiment label
        if total_posts > 0:
            positive_percentage = (positive_count / total_posts) * 100
            negative_percentage = (negative_count / total_posts) * 100
            neutral_percentage = (neutral_count / total_posts) * 100
        else:
            positive_percentage = negative_percentage = neutral_percentage = 0

        # Append the user's sentiment data to the list
        users_data.append({
            'user': user.username,
            'positive_percentage': positive_percentage,
            'negative_percentage': negative_percentage,
            'neutral_percentage': neutral_percentage,
        })

    # Return the sentiment data as JSON
    return JsonResponse({
        'users_data': users_data,
    })

def get_opposing_sentiment_posts(request, sentiment):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=403)
    
    # get the opposite sentiment for each user
    if sentiment == 'positive':
        sentiment_filter = 'Negative'
    elif sentiment == 'negative':
        sentiment_filter = 'Positive'
    elif sentiment == 'neutral':
        sentiment_filter = 'Neutral'
    else:
        return JsonResponse({'error': 'Invalid sentiment'}, status=400)

    # Filter posts by sentiment and exclude posts by the current user
    posts = Post.objects.filter(sentiment_label=sentiment_filter).exclude(user=request.user)

    posts_data = [
        {
            'id': post.id,
            'uuid': post.uuid,
            'content': post.content,
            'user': post.user.username,
            'created_at': post.created_at.isoformat(),
            'likes': post.liked_by.count(),
            'dislikes': post.disliked_by.count(),
            'sentiments': post.sentiment_label,
            'comments': [
                {
                    'id': comment.id,
                    'content': comment.content,
                    'user': comment.user.username,
                    'created_at': comment.created_at.isoformat(),
                }
                for comment in post.comments.all()
            ],
        }
        for post in posts
    ]

    return JsonResponse({'posts': posts_data})

def get_ordered_posts(request, order_type):
    if order_type == 'popular':
        posts = Post.objects.order_by('-liked_by')  #order by likes for most popular content
    elif order_type == 'recent':
        posts = Post.objects.order_by('-created_at')  # Order by creation date for most recent
    elif order_type == 'controversial':
        posts = Post.objects.order_by('-disliked_by') #order by dilikes for most controversial  content
    else:
        posts = Post.objects.all()  
    posts_data = [
        {
            'id': post.id,
            'uuid': post.uuid,
            'content': post.content,
            'user': post.user.username,
            'created_at': post.created_at.isoformat(),
            'likes': post.liked_by.count(),
            'dislikes': post.disliked_by.count(),
            'sentiments': post.sentiment_label,
            'comments': [
                {
                    'id': comment.id,
                    'content': comment.content,
                    'user': comment.user.username,
                    'created_at': comment.created_at.isoformat(),
                }
                for comment in post.comments.all()
            ],
        }
        for post in posts
    ]
    return JsonResponse({'posts': posts_data})



