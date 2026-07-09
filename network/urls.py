
from django.urls import path

from . import views

urlpatterns = [
    # Autenticación
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # Posts
    path("create", views.create_post, name="create"),
    path("all_posts", views.all_posts, name="all_posts"),
    path("following", views.following, name="following"),

    # Perfil
    path("profile/<str:username>", views.profile , name="profile"),
    path("follow/<str:username>", views.follow_toggle, name="follow_toggle"),

    # Interacciones
    path("like/<int:post_id>", views.like_post, name="like_post"),
    path("edit/<int:post_id>", views.edit_post, name="edit_post")
]
