from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    year = models.IntegerField(null=True, blank=True)
    department = models.CharField(max_length=50)
    
class Post(models.Model):
    CATEGORY_CHOICES = [
        (1, 'Match Updates'),
        (2, 'Team News'),
        (3, 'Player Stats'),
        (4, 'Fan Discussions'),
        (5, 'Memes'),
        (6, 'Points Table'),
        (7, 'Teams')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    caption = models.TextField()
    post_image = models.FileField(upload_to='posts/', null=True, blank=True)
    likes = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    category = models.IntegerField(choices=CATEGORY_CHOICES)
    department = models.CharField(max_length=50) 
    year = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, related_name="replies", null=True, blank=True
    )
    def is_parent(self):
        return self.parent is None

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_save = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} saved {self.post.title}"
    