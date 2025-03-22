from django.db import models
from accounts.models import CustomUser
import uuid

class Post(models.Model):
    # User who created the post
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='posts')
    # Actual Post content
    content = models.TextField()
    # Timestamp when the post was created
    created_at = models.DateTimeField(auto_now_add=True)
    # Unique identifier for the post 
    uuid = models.CharField(max_length=255, unique=True, default=uuid.uuid4, editable=False)
    # Users who liked the post
    liked_by = models.ManyToManyField('accounts.CustomUser', related_name='liked_posts', blank=True)
    # Users who disliked the post
    disliked_by = models.ManyToManyField('accounts.CustomUser', related_name='disliked_posts', blank=True)
    # Vader Sentiment score
    sentiment_label = models.CharField(max_length=10, null=True, blank=True) 
    sentiment_score = models.FloatField(null=True, blank=True)  
    # Sentiment preferences
    positive_percentage = models.FloatField(default=0.0)
    negative_percentage = models.FloatField(default=0.0)
    neutral_percentage = models.FloatField(default=0.0)


    def __str__(self):
        return f"Post by {self.user.username} on {self.created_at}"

    class Meta:
        ordering = ['-created_at']  # Order posts by the most recent initially

    @property
    def likes_count(self):
        return self.liked_by.count()

    @property
    def dislikes_count(self):
        return self.disliked_by.count()


class Comment(models.Model):
    # Foreign key to the Post model to associate a comment with a post
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    # User who created the comment
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    # Actual c ontent of the comment
    content = models.TextField()
    # Timestamp of ewhen the comment was created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on Post {self.post.id}"

    class Meta:
        ordering = ['-created_at']  # Order comments by the most recent
