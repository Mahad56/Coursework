# Generated by Django 5.1.7 on 2025-03-18 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0006_alter_post_sentiment_score"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="post",
            name="sentiment_score",
        ),
        migrations.AddField(
            model_name="post",
            name="sentiment_label",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
