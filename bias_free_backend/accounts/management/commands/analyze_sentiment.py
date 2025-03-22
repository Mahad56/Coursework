import nltk
nltk.download('vader_lexicon')
from django.core.management.base import BaseCommand
from posts.models import Post
from nltk.sentiment.vader import SentimentIntensityAnalyzer

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        sid = SentimentIntensityAnalyzer()

        posts = Post.objects.filter(sentiment_label__isnull=True)  # analyse only posts that don't have a sentiment label
        updates = []

        for post in posts:
            sentiment = sid.polarity_scores(post.content)# Analyse the sentiment of the post 
            compound_score = sentiment['compound']
    
            # Determine the sentiment of each post, https://akladyous.medium.com/sentiment-analysis-using-vader-c56bcffe6f24#:~:text=Notice%20that%20the,compound%20score%3C%3D%2D0.05
            if compound_score >= 0.05:
                sentiment_label = "Positive" 
            elif compound_score <= -0.05:
                sentiment_label = "Negative"
            else:
                sentiment_label = "Neutral"
        
            post.sentiment_label = sentiment_label 
            post.sentiment_score = compound_score  
            updates.append(post)

        Post.objects.bulk_update(updates, ['sentiment_label', 'sentiment_score'])
            
