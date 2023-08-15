from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

def validate_image_size(value):
    limit = 3 * 1024 * 1024  # 3MB limit
    if value.size > limit:
        raise ValidationError(f"File size exceeds the limit of 3MB.")



class Post(models.Model):
    author = models.ForeignKey(User,on_delete=models.CASCADE, related_name='author' )
    content = models.CharField(max_length=140)
    date = models.DateTimeField(auto_now_add=True)
    image_cover = models.ImageField(upload_to='img/',null=True, validators=[FileExtensionValidator(['jpg', 'jpeg', 'png']), validate_image_size])
    def __str__(self) -> str:
        return f"Post {self.id} made by {self.author} on {self.date.strftime('%d %b %Y %H:%M:%S')}"

    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post")
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self) -> str:
        return f"Comment {self.id} made by {self.user} on {self.post.id} at {self.date.strftime('%d %b %Y %H:%M:%S')}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    
class Dislike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='dislikes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="dislikes")

class Follow(models.Model):
    current_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    second_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    each_other = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Check if the users follow each other
        if self.current_user.following.filter(id=self.second_user.id).exists() and \
                self.second_user.following.filter(id=self.current_user.id).exists():
            self.each_other = True
        else:
            self.each_other = False

        super().save(*args, **kwargs)
