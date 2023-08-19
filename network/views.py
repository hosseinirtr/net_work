from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Count
from django.core.paginator import Paginator
from .models import User, Post, Follow


def index(request):
    posts = Post.objects.all().order_by('-date')

    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "posts":posts,
        "posts_of_the_page":posts_of_the_page
    })


@login_required
def add_post(request):
    print("request" , request)
    if request.method == "POST":
        user = request.user
        # user = User.objects.get(pk=request.user.id)
        content = request.POST['content']
        if request.FILES:
            image = request.FILES['image']
        else:
            image = None

        post = Post(author=user, content=content, image_cover=image)
        post.save()
        return HttpResponseRedirect(reverse(index))




def profile(request, username):
    user =User.objects.get(username=username) 
    posts = Post.objects.filter(author=user).order_by('-date')
    following = Follow.objects.filter(current_user = user)
    followers = Follow.objects.filter(second_user = user)
    user_profile = user
    checkFollow = Follow.objects.filter(current_user=user, second_user = user)
    print(checkFollow)    
    checkFollow = Follow.objects.filter(current_user=request.user, second_user = user)
    isFollowing = True if len(checkFollow) != 0 else False

    return render(request, "network/profile.html", {
        "posts_of_the_page":posts,
        'username':user.username,
        "following":following,
        "followers":followers,
        "isFollowing":isFollowing,
        "user_profile":user_profile
        
    })


def follow(request):
    if request.method == "POST":
        id = User.objects.get(username = request.POST['username']).id
        user = request.user
        second_user =User.objects.get(pk = id)
        follow_method = Follow(current_user=user, second_user=second_user)
        follow_method.save()
        return HttpResponseRedirect(reverse(profile, kwargs={"username":second_user.username}))


def unfollow(request):
    if request.method == "POST":
        id = User.objects.get(username = request.POST['username']).id
        user = request.user
        second_user =User.objects.get(pk = id)
        follow_method = Follow.objects.get(current_user=user, second_user=second_user)
        print("current_user=",user, 'second_user=',second_user)
        print(follow_method)
        follow_method.delete()
        return HttpResponseRedirect(reverse(profile, kwargs={"username":second_user.username}))

def following_post(request):
    current_user = request.user
    follow_list = Follow.objects.get(current_user=current_user)
    post_of_follower = Post.objects.filter(author__in = follow_list)
    print(post_of_follower)
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
