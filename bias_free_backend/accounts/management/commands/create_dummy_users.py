from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from posts.models import Post, Comment


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        # 5 dummy users
        users_data = [
            {"username": "user1", "password": "password123", "email": "user1@example.com"},
            {"username": "user2", "password": "password123", "email": "user2@example.com"},
            {"username": "user3", "password": "password123", "email": "user3@example.com"},
            {"username": "user4", "password": "password123", "email": "user4@example.com"},
            {"username": "user5", "password": "password123", "email": "user5@example.com"},
        ]
        #I've given each of the users 5 dummy posts with varying sentiments
        user_posts = {
            "user1": [
                "Proud of the recent healthcare reform. 💙",
                "Today has not been a good day.",
                "Just finished a 5K run. Feeling amazing!",
                "Tried a new recipe today. It turned out perfect!",
                "Got so many chores done today."
            ],
            "user2": [
                "Frustrated with the state of our political system. 😡",
                "So glad to welcome my son to the world today!",
                "Does anyone have a guide for indoor gardening?",
                "Why does technology always fail at the worst times?",
                "My little one just said their first word!"
            ],
            "user3": [
                "Interesting debates about our country’s direction.",
                "Can’t believe this movie gets rave reviews. 😡",
                "Thinking about adopting another pet.",
                "Drowning in deadlines. Wish I could catch a break. 😩",
                "Tried making homemade pasta today. Chef in the making?"
            ],
            "user4": [
                "Climate change is pushing us toward disaster.",
                "Today has not been a good day.",
                "Finished reading The Hunger Games. It was okay.",
                "Barely got any sleep last night.",
                "Finished my DIY bookshelf today. Turned out great!"
            ],
            "user5": [
                "The alarming drop in birth rates is troubling.",
                "Cats are better than dogs.",
                "The meeting is at 2 pm today.",
                "Planning a road trip next weekend. Suggestions?",
                "Had to fill up the car with gas today. Prices seem stable."
            ]
        }
        #every user has a custom message that is then mapped to a post 
        comments_map = {
            "user1": [
                ["I appreciate your optimism!", "We need to focus on more immediate challenges.", "Great post!"],
                ["Hang in there!", "Hope things get better for you soon.", "Stay strong!"],
                ["Inspiring!", "Keep it up!", "Way to go!"],
                ["Cooking is so therapeutic.", "What recipe did you try?", "Sounds delicious!"],
                ["Chores are never-ending, but satisfying when done.", "Same here!", "Productive day!"]
            ],
            "user2": [
                ["Completely agree!", "Leadership needs to step up.", "What a mess!"],
                ["Congratulations!", "Such a blessing!", "Best wishes to you and your family!"],
                ["Check online forums.", "Pinterest has great resources.", "Good luck with your project!"],
                ["Technology can be so unreliable.", "I feel your pain.", "It happens to the best of us."],
                ["That’s a special moment!", "So cute!", "Cherish these memories!"]
            ],
            "user3": [
                ["Great perspective.", "Open-mindedness is key.", "Thought-provoking post."],
                ["Couldn’t agree more.", "Thanks for sharing your thoughts.", "What a disappointment!"],
                ["Pets bring so much joy.", "Adoption is a noble choice.", "Good luck!"],
                ["Take a break if you can.", "Deadlines are tough.", "You’ve got this!"],
                ["Homemade pasta is the best!", "Sounds like fun.", "Bon appétit!"]
            ],
            "user4": [
                ["The urgency is real.", "We need action now!", "What can we do to help?"],
                ["Hope things improve for you.", "We all have bad days.", "Stay positive!"],
                ["The book has its moments.", "What did you think of the ending?", "Not for everyone."],
                ["Sleep is so important.", "Hope you catch up on rest soon.", "Caffeine to the rescue!"],
                ["DIY projects are so rewarding.", "Great job!", "What’s next?"]
            ],
            "user5": [
                ["This is a critical issue.", "Spot on.", "Governments need to act now."],
                ["Dogs are better!", "Agreed!", "Both have their charm."],
                ["Thanks for the reminder!", "Don’t forget to set an alarm.", "Noted."],
                ["The open road is calling!", "Try a national park.", "Have fun!"],
                ["Gas prices fluctuate so much.", "Lucky you!", "Hope it stays that way."]
            ]
        }

        
        users = []
        for user_data in users_data:
            user = CustomUser.objects.create_user(
                username=user_data["username"],
                password=user_data["password"],
                email=user_data["email"]
            )
            user.save()
            users.append(user)

        for user in users:
            posts_content = user_posts[user.username]
            post_comments = comments_map[user.username]

            for idx, content in enumerate(posts_content):
                # Create post
                post = Post.objects.create(user=user, content=content)
                post.save()

                # Add comments to the post from other users
                for commenter, comment_content in zip(
                    [u for u in users if u != user],
                    post_comments[idx]
                ):
                    comment = Comment.objects.create(
                        post=post, user=commenter, content=comment_content
                    )
                    comment.save()

        self.stdout.write(self.style.SUCCESS("Dummy users, posts, and comments created successfully."))
