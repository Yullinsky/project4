from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    body = models.TextField(max_length=640)
    date_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    def __str__(self):
        return f"{self.user.username}: {self.body[:50]}"
    
    def total_likes(self):
        return self.likes.count()

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")

    class Meta:
        unique_together = ['follower', 'followed']
    
    def __str__(self):
        return f"{self.follower} follows {self.followed}"
'''
class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Followers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Comments(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios')
    text = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
'''
# You will also need to add additional models to this file to represent details about posts, likes, and followers
# Remember that each time you change anything in network/models.py, you’ll need to first run python manage.py makemigrations and then python manage.py migrate to migrate those changes to your database