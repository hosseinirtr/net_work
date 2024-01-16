import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Count
from django.core.paginator import Paginator
from .models import User, Post, Follow, Like
from django.http import JsonResponse


def like(request, id):
    try:
        post = Post.objects.get(pk=id)
        user = request.user

        try:
            is_liked = Like.objects.get(post=post, user=user)
            is_liked.delete()
            action = 'Disliked'
        except Like.DoesNotExist:
            like_method = Like(post=post, user=user)
            like_method.save()
            action = 'Liked'

        return JsonResponse({'success': f'Post {action}', 'action': action})

    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)


def edit_post(request, id):
    if request.method == "POST":
        data = json.loads(request.body)
        edit_post_ = Post.objects.get(pk=id)
        edit_post_.content = data["content"]
        edit_post_.save()
        return JsonResponse({"message": "Successes received data ", "data": data["content"]})


def index(request):
    posts_of_the_page =[]
    user_liked_id = []
    if request.user.is_authenticated:
        posts = Post.objects.all().order_by('-date').annotate(
            num_likes=Count('likes'),
            num_dislikes=Count('dislikes'),
        )
        # Pagination
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        posts_of_the_page = paginator.get_page(page_number)

        user_liked = Like.objects.filter(user=request.user).filter(
            post__in=posts_of_the_page)
        user_liked_id = [like.post.id for like in user_liked]
    return render(request, "network/index.html", {
        "posts_of_the_page": posts_of_the_page,
        "user_liked_id": user_liked_id
    })


@login_required
def following_page(request):
    user = request.user
    following = Follow.objects.filter(
        current_user=user).values_list('second_user', flat=True)
    posts_of_the_page = Post.objects.filter(
        author__in=following)
    return render(request, "network/following.html", {
        "posts_of_the_page": posts_of_the_page
    })


@login_required
def add_post(request):
    print("request", request)
    if request.method == "POST":
        user = request.user
        content = request.POST['content']
        if request.FILES:
            image = request.FILES['image']
        else:
            image = None

        post = Post(author=user, content=content, image_cover=image)
        post.save()
        return HttpResponseRedirect(reverse(index))


@login_required
def profile(request, username):
    user = User.objects.get(username=username)
    posts = Post.objects.filter(author=user).order_by('-date').annotate(
        num_likes=Count('likes'),
        num_dislikes=Count('dislikes')
    )
    following = Follow.objects.filter(current_user=user)
    followers = Follow.objects.filter(second_user=user)
    user_profile = user
    checkFollow = Follow.objects.filter(current_user=user, second_user=user)
    print(checkFollow)
    checkFollow = Follow.objects.filter(
        current_user=request.user, second_user=user)
    isFollowing = True if len(checkFollow) != 0 else False

    return render(request, "network/profile.html", {
        "posts_of_the_page": posts,
        'username': user.username,
        "following": following,
        "followers": followers,
        "isFollowing": isFollowing,
        "user_profile": user_profile

    })


@login_required
def follow(request):
    if request.method == "POST":
        id = User.objects.get(username=request.POST['username']).id
        user = request.user
        second_user = User.objects.get(pk=id)
        follow_method = Follow(current_user=user, second_user=second_user)
        follow_method.save()
        return HttpResponseRedirect(reverse(profile, kwargs={"username": second_user.username}))


@login_required
def unfollow(request):
    if request.method == "POST":
        id = User.objects.get(username=request.POST['username']).id
        user = request.user
        second_user = User.objects.get(pk=id)
        follow_method = Follow.objects.get(
            current_user=user, second_user=second_user)
        print("current_user=", user, 'second_user=', second_user)
        print(follow_method)
        follow_method.delete()
        return HttpResponseRedirect(reverse(profile, kwargs={"username": second_user.username}))


def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

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


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

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
