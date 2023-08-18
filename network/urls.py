
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("post", views.add_post, name="post"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("following", views.follow, name="following"),
    path("unfollowing", views.unfollow, name="unfollowing"),
    path("following_page", views.following_page, name="following_page"),
    path("edit_post/<str:id>", views.edit_post, name="edit_post"),
    # path('get_liked_users/<int:post_id>/',
    #      views.get_liked_users, name='get_liked_users'),
    path('like/<int:id>', views.like, name="like")


]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
