from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from posts.models import Post, Comment


class Command(BaseCommand):
    help = 'Create 5 dummy user accounts, each with a distinct post and comments from other users'

    def handle(self, *args, **kwargs):
        users_data = [
            {"username": "user1", "password": "password123", "email": "user1@example.com"},
            {"username": "user2", "password": "password123", "email": "user2@example.com"},
            {"username": "user3", "password": "password123", "email": "user3@example.com"},
            {"username": "user4", "password": "password123", "email": "user4@example.com"},
            {"username": "user5", "password": "password123", "email": "user5@example.com"},
        ]

        user_content = {
            "user1": (
                "I am so proud to see the strides our country has made in the last few years. The recent healthcare reform is a game changer, making it easier for families to access affordable care. 💙 The investments in renewable energy are also paying off, and it's so refreshing to see real progress in combating climate change. 🌍 Our economy is showing signs of resilience, and job growth is at a record high, which has positively impacted communities across the nation. These initiatives reflect the commitment of our leaders to ensure a better future for all. It's inspiring to see that with the right policies, we can move toward a more inclusive, sustainable, and prosperous future. I'm optimistic about what lies ahead, and I believe our best days are still ahead of us! 🙌"
            ),
            "user2": (
                "I am deeply frustrated with the state of our political system right now. It feels like nothing is getting done in Washington, and the gridlock is unbearable. The constant bickering between parties has turned into a toxic environment, and it’s ordinary citizens who are suffering. The recent budget cuts to public services have had devastating effects on our most vulnerable communities, and yet, politicians seem more focused on personal power plays than addressing real issues. The lack of progress on crucial matters like climate change, healthcare reform, and income inequality is appalling. Every time I turn on the news, it’s just more division, more lies, and no accountability. It’s disheartening to see how disconnected our government has become from the needs of the people. We deserve better leadership. 😡"
            ),
            "user3": (
                "There’s been a lot of debate lately about the direction our country is headed in, and it's clear that people have strong opinions on both sides. On one hand, there have been some policies passed recently that have created economic growth and provided new opportunities in certain industries. On the other hand, there are also concerns about the growing divide between political parties, and some decisions are still up for discussion. Healthcare reform, immigration, and climate change are all topics that remain high on the agenda. It’s an interesting time in politics, as there are many different perspectives at play. Ultimately, the outcomes of these debates will shape the future, but it’s important to keep an open mind as the discussions unfold. Let's see what comes out of it all."
            ),
            "user4": (
                "The world is slowly deteriorating, and the rapid pace of climate change is pushing us closer to an irreversible disaster. The extreme weather patterns, rising sea levels, and wildfires that seem to get worse every year are undeniable signs of a planet in peril. Governments have failed to take meaningful action, and the environment continues to suffer as industries prioritize profit over the health of the planet. Fossil fuel consumption is still rampant, and the world seems to be accelerating toward a tipping point that could spell catastrophe for future generations. It's incredibly frustrating to see the lack of urgency and the constant inaction from world leaders when the future of humanity is on the line. The clock is ticking, and we’re running out of time."
            ),
            "user5": (
                "The alarming drop in birth rates across the world is a wake-up call that we simply can't ignore. As societies become increasingly urbanized, the idea of having children is seen as less of a priority, and economic pressures only make it harder for families to grow. What’s even more troubling is that this demographic shift is leading to a rapidly aging population, putting even more strain on healthcare systems and the workforce. The future looks bleak with fewer young people to support an ever-growing elderly population. Governments are either slow to address this issue or too focused on short-term policies that do nothing to reverse the trend. We’re heading towards a society where the cycle of life could be disrupted, and the consequences of such a demographic crisis will affect generations to come."
            )
        }

        # Comments for each user's post
        comment_map = {
            "user1": {
                "user2": "I agree with your optimism, but there are still so many challenges we face.",
                "user3": ":)",
                "user4": "While progress is happening, user1, we cannot ignore the climate crisis.",
                "user5": "User1, your point is valid, but demographic issues might impact this optimism."
            },
            "user2": {
                "user1": "User2, I feel your frustration, but we must keep pushing for change.",
                "user3": "You’re right, user2. The lack of accountability is alarming.",
                "user4": "The political system has failed us in many ways, user2. You’re spot on.",
                "user5": "User2, I empathize. Leadership needs to focus on long-term solutions."
            },
            "user3": {
                "user1": "Great balanced take, user3. We need more voices like yours in the conversation.",
                "user2": "You’re right, user3. Open minds are crucial for meaningful progress.",
                "user4": "Step outside. @£$£$",
                "user5": "We NEED to go back to having more kids!!"
            },
            "user4": {
                "user1": "Absolutely, user4. We need immediate action to save the planet.",
                "user2": "User4, I completely agree. The inaction on climate change is disgraceful.",
                "user3": "You’ve highlighted critical points, user4. The time to act is now.",
                "user5": "User4, your post is a wake-up call. Thank you for voicing this."
            },
            "user5": {
                "user1": "Your concern, user5, is valid. The birth rate issue is a pressing problem.",
                "user2": "User5, I share your worries about the aging population’s impact on society.",
                "user3": "Interesting take, user5. This demographic shift needs urgent attention.",
                "user4": "User5, your post sheds light on an issue many overlook."
            }
        }

        # Create users
        users = []
        for user_data in users_data:
            user = CustomUser.objects.create_user(
                username=user_data["username"],
                password=user_data["password"],
                email=user_data["email"]
            )
            user.save()
            users.append(user)

        # Create posts and comments
        for user in users:
            content = user_content.get(user.username, f"This is a unique post by {user.username}.")
            post = Post.objects.create(user=user, content=content)
            post.save()

            # Add comments from other users
            for commenter in users:
                if commenter.username != user.username:
                    comment_content = comment_map.get(user.username, {}).get(
                        commenter.username,
                        f"Generic comment from {commenter.username} on {user.username}'s post."
                    )
                    comment = Comment.objects.create(post=post, user=commenter, content=comment_content)
                    comment.save()
                    self.stdout.write(f"Comment by {commenter.username} on {user.username}'s post: {comment_content}")

        self.stdout.write(self.style.SUCCESS("Dummy users, posts, and comments created successfully."))
