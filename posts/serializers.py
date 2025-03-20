from rest_framework import serializers
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from .models import Post, Comment, Notification, SavedPost, Student

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        user = User.objects.filter(username=username).first()
        
        
        if not user:
            raise serializers.ValidationError({'username': 'Invalid username'})

        if not check_password(password, user.password):
            raise serializers.ValidationError({'password': 'Invalid password'})
        print(user.username)
        print(check_password(password,user.password))

        return {'user': user}
    
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class HomePostsSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = '__all__'
        
    def get_comments_count(self, obj):
        print(obj)
        return obj.comments.count()
             
        
class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'created_at', 'parent', 'replies']

    def get_replies(self, obj):
        replies = obj.replies.all() 
        return CommentSerializer(replies, many=True).data if replies.exists() else []

class PostDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    comments = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ['id', 'title', 'caption','user', 'post_image', 'likes', 'comments_count', 'category',  'created_at', 'comments']
    def get_comments(self, obj): 
        comments = obj.comments.filter(parent__isnull=True)
        return CommentSerializer(comments, many=True).data
    
class CommentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['post',  'content', 'parent']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'comment', 'message', 'is_read', 'created_at']
        
        
class UplaodPostSerializer(serializers.ModelSerializer):
    user = CommentUserSerializer(read_only=True)
    class Meta:
        model = Post
        fields = ['user','title', 'caption', 'post_image', 'category', 'department', 'year']
        

class DisplayPosts(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'caption','title', 'post_image', 'category']    
        
class SavedPostSerializer(serializers.ModelSerializer):
    user = CommentUserSerializer(read_only = True)
    class Meta:
        model = SavedPost
        fields = ['id', 'user', 'post', 'created_at', 'updated_at', 'is_save']
    
    def validate(self, validate_data):
        post = validate_data.get('post')
        user = self.context['request'].user
        if post is None:
            raise serializers.ValidationError("Post does not exist")
        post_obj = SavedPost.objects.filter(post = post, user = user).exists()
        if post_obj:
            raise serializers.ValidationError("You have already saved this post.")
        return validate_data


class DisplaySavedPostSerializer(serializers.ModelSerializer):
    user = CommentUserSerializer(read_only = True)
    post = DisplayPosts()
    class Meta:
        model = SavedPost
        fields = ['id', 'user', 'post', 'created_at', 'updated_at', 'is_save']
        

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['department', 'year']
        
class ProfileSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer()
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'last_login', 'date_joined','student']

class RegisterSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer()
    class Meta:
        model = User
        fields = ['username','password','student']
        
    def create(self, validated_data):
        student_data = validated_data.pop('student')
        user = User.objects.create(**validated_data)
        Student.objects.create(user = user, **student_data)
        return user
    
class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not check_password(value, user.password):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("New password must be at least 8 characters long.")
        return value