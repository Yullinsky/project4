from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import User, Post, Follow


def index(request):
    posts = Post.objects.all().order_by('-date_time')
    return render(request, "network/index.html", {
        "posts": posts
    })


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

@login_required
def create_post(request):
    if request.method == "POST":
        body = request.POST.get("body")
        title = request.POST.get("title")

        if not body or not title:
            return HttpResponseRedirect(reverse("index"))
        
        post = Post(
            user=request.user,
            title=title,
            body=body
        )
        post.save()

        return HttpResponseRedirect(reverse("index"))
    return render(request, "network/create.html")

def profile(request, username):
    usuario = User.objects.get(username=username)
    publicaciones = Post.objects.filter(user=usuario).order_by("-date_time")
    return render(request, "network/profile.html", {
        "perfil": usuario,
        "posts": publicaciones
    })

def follow(request, username):
    target_user = get_object_or_404(User, username=username)

    if request.user == target_user:
        return HttpResponseRedirect(reverse("profile", kwargs={"username": username}))
    
    follow_exists = Follow.object.filter(
        user=request.user,
        following=target_user
    ).exists()

    if follow_exists:
        Follow.objects.filter(user=request.user, following=target_user).delete()
    else:
        new_follow = Follow(user=request.user, following=target_user)
        new_follow.save()
    
    return HttpResponseRedirect(reverse("profile", kwargs={"username": username}))
