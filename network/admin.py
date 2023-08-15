from django.contrib import admin
from .models import Post, User, Comment , Like, Dislike, Follow


# Register your models here.
admin.site.register(Post)
admin.site.register(User)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Dislike)
admin.site.register(Follow)
# admin.register.site(Post)