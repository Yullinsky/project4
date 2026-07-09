from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

import json

from .models import User, Post, Follow
from .helpers import paginate

# Autenticación
def index(request):
    page_obj = paginate(request, Post.objects.all().order_by('-date_time'))
    return render(request, "network/index.html", {"page_obj": page_obj})

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


# Posts
@login_required
def create_post(request):
    if request.method == "POST":
        body = request.POST.get("body", "").strip()

        if not body:
            return render(request, "network/create.html", {
                "error": "Post cannot be empty"
            })
        
        new_post = Post(
            user=request.user,
            body=body
        )
        new_post.save()

        return HttpResponseRedirect(reverse("index"))
    return render(request, "network/create.html")

def all_posts(request):
    page_obj = paginate(request, Post.objects.all().order_by('-date_time'))
    return render(request, "network/all_posts.html", {"page_obj": page_obj})

@login_required
def following(request):
    following_users = Follow.objects.filter(follower=request.user).values_list('followed', flat=True)
    posts = Post.objects.filter(user__in=following_users).order_by('-date_time')
    
    page_obj = paginate(request, posts)

    return render(request, "network/following.html", {"page_obj": page_obj})

# Perfil
def profile(request, username):
    usuario = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=usuario).order_by("-date_time")
    page_obj = paginate(request, posts)

    return render(request, "network/profile.html", {
        "perfil": usuario,
        "page_obj": page_obj
    })

@login_required
def follow_toggle(request, username):
    user_to_follow = get_object_or_404(User, username=username)

    if request.user == user_to_follow:
        return JsonResponse({"error": "Cannot follow yourself"}, status=400)
    
    if request.method == "POST":
        follow_obj = Follow.objects.filter(
            follower=request.user,
            followed=user_to_follow
        )

        if follow_obj.exists():
            follow_obj.delete()
            is_following = False
        else:
            Follow.objects.create(
                follower=request.user,
                followed=user_to_follow
            )
            is_following = True
    
        return JsonResponse({
            "is_following": is_following,
            "followers_count": user_to_follow.followers.count()
        })
    
    return JsonResponse({"error": "Invalid request"}, status=400)

# Interacciones
@csrf_exempt
@login_required
def like_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)

    if request.method == "POST":
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
        
        return JsonResponse({
            "likes": post.total_likes(),
            "liked": liked
        })
    return JsonResponse({"error": "Invalid method"}, status=405)

@csrf_exempt
@login_required
def edit_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)

    if post.user != request.user:
        return JsonResponse({"error": "Not authorized"}, status=403)

    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            content = data.get("content", "").strip()

            if content:
                post.body = content
                post.save()
                return JsonResponse({
                    "success": True,
                    "content": post.body,
                    "timestamp": post.date_time.strftime("%B %d, %Y, %I:%M %p")
                })
            else:
                return JsonResponse({"error": "Content cannot be empty"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Invalid method"}, status=405)