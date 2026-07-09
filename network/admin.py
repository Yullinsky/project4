from django.contrib import admin
from .models import User, Post, Follow

# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'body', 'date_time', 'total_likes')
    list_filer = ('date_time', 'user')
    search_fields = ('body', 'user__username')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'followed')
    list_filter = ('follower', 'followed')