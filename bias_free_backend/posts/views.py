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


def post_list(request):
    # Use prefetch_related to reduce database queries
    posts = Post.objects.prefetch_related('comments', 'liked_by', 'disliked_by').all()  # Adjust to your model relations
    posts_data = []

    # Iterate through the posts and add comments persistently
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
            ],
        }
        posts_data.append(post_data)

    return render(request, 'posts/posts_list.html', {'posts': posts_data})

@csrf_exempt
def create_post(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            post_content = data.get('content', '')

            if post_content:
                # Create and save a new post
                new_post = Post(content=post_content, user=request.user)
                new_post.save()

                # Return success response with the created post data
                return JsonResponse({
                    'message': 'Post created successfully',
                    'id': new_post.id,
                    'uuid': new_post.uuid,
                    'content': new_post.content,
                    'user': request.user.username,
                    'likes': new_post.liked_by.count(),  # Using count() to get the number of likes
                    'dislikes': new_post.disliked_by.count(),  # Similarly, count dislikes
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


    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        if request.user not in post.liked_by.all():
            post.liked_by.add(request.user)
            post.disliked_by.remove(request.user)  # Optional: Remove dislike if the user had disliked it
            post.save()
            return JsonResponse({'message': 'Post liked successfully.', 'likes': post.likes_count})
        return JsonResponse({'error': 'You already liked this post.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@login_required
@csrf_exempt
def create_comment(request, post_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content')

            if not content:
                return JsonResponse({'error': 'Comment content is required.'}, status=400)

            post = Post.objects.get(id=post_id)

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

        # Add the user to the liked_by relationship if they haven't liked already
        if request.user not in post.liked_by.all():
            post.liked_by.add(request.user)  # Adds the user to the likes
            post.save()

        return JsonResponse({'message': 'Post liked successfully', 'likes': post.liked_by.count()})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def dislike_post(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)

        # Add the user to the disliked_by relationship if they haven't disliked already
        if request.user not in post.disliked_by.all():
            post.disliked_by.add(request.user)  # Adds the user to the dislikes
            post.save()

        return JsonResponse({'message': 'Post disliked successfully', 'dislikes': post.disliked_by.count()})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def remove_like_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        if request.user in post.liked_by.all():
            post.liked_by.remove(request.user)
            post.save()
            return JsonResponse({'message': 'Like removed successfully.', 'likes': post.liked_by.count()})
        return JsonResponse({'error': 'You have not liked this post.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def remove_dislike_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        if request.user in post.disliked_by.all():
            post.disliked_by.remove(request.user)
            post.save()
            return JsonResponse({'message': 'Dislike removed successfully.', 'dislikes': post.disliked_by.count()})
        return JsonResponse({'error': 'You have not disliked this post.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

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




    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        if request.user in post.disliked_by.all():
            post.disliked_by.remove(request.user)
            post.save()
            return JsonResponse({'message': 'Dislike removed successfully.', 'dislikes': post.dislikes_count})
        return JsonResponse({'error': 'You have not disliked this post.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        if request.user in post.disliked_by.all():  # Assuming a many-to-many field for dislikes
            post.disliked_by.remove(request.user)
            post.save()
            return JsonResponse({'message': 'Dislike removed successfully.', 'dislikes': post.disliked_by.count()})
        return JsonResponse({'error': 'You have not disliked this post.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)