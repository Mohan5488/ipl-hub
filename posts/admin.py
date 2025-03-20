from django.contrib import admin
from .models import Student, Post, Comment,Notification, SavedPost
# Register your models here.
admin.site.register(Student)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Notification)
admin.site.register(SavedPost)