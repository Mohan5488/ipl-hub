from rest_framework.views import APIView, Response
from .models import Student, Post, Comment, Notification, SavedPost
from .serializers import  LoginSerializer, HomePostsSerializer, PostDetailSerializer, CommentCreateSerializer, NotificationSerializer, UplaodPostSerializer, SavedPostSerializer, ProfileSerializer, RegisterSerializer, DisplayPosts, DisplaySavedPostSerializer, ChangePasswordSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from django.utils.timezone import now
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            user_obj = User.objects.get(username=user)
            student = Student.objects.filter(user=user).first()
            user.last_login = now()  
            user.save(update_fields=['last_login'])  
            is_default_password = check_password("Default@123", user_obj.password)
            return Response({
                'message': 'Login successful',
                'username': user.username,
                'dept': student.department if student else None,
                'year': student.year if student else None,
                'token': token.key,
                'fullname' : user_obj.first_name,
                "is_default_password": is_default_password
            }, status=200)
        return Response({'message': serializer.errors}, status=400)
    
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.password = make_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class DashboardViewSet(APIView):
    permission_classes = [IsAuthenticated]  
    authentication_classes = [TokenAuthentication]
    def get(self, request):
        return Response({"message": f"Hello, {request.user.username}!"}, status=status.HTTP_200_OK)

class CategoryFeedView(APIView):
    def get(self, request,dept, year, category):
        students = Student.objects.filter(department=dept, year=year).values_list('user', flat=True)
        post_filter = Post.objects.filter(user__in=students)

        if int(category) != 0:
            posts = post_filter.filter(category=category).order_by('-created_at')[:20]
            serializer = HomePostsSerializer(posts, many=True)
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            posts = post_filter.all().order_by('-created_at')[:20]
            serializer = HomePostsSerializer(posts, many=True)
            return Response({'data':serializer.data}, status=status.HTTP_200_OK)
        
class PostView(viewsets.ModelViewSet):
    serializer_class = PostDetailSerializer
    queryset = Post.objects.all()
    
    def list(self, request):
        id = request.GET.get('id')
        if id:
            queryset = self.get_queryset().filter(id=id)
            serializer = PostDetailSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    def delete(self, request):
        id = request.GET.get('id')
        if id:
            post = Post.objects.get(id = id)
            post.delete()
            return Response({'message' : "Post deleted successfully"}, status=status.HTTP_200_OK)
        return Response({"message" : "Post doesnot exists"}, status=status.HTTP_400_BAD_REQUEST)

class AddCommentView(APIView):
    permission_classes = [IsAuthenticated]  
    authentication_classes = [TokenAuthentication]
    def post(self, request):
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(user=request.user)
            post = comment.post
            notifications = []
            if post.user != request.user:
                notifications.append(
                    Notification(
                        user=post.user,
                        comment=comment,
                        message=f"{request.user.username} commented on your post: '{comment.content}'"
                    )
                )
            if comment.parent:
                parent_user = comment.parent.user  
                if parent_user != request.user and parent_user != post.user:
                    notifications.append(
                        Notification(
                            user=parent_user,
                            comment=comment,
                            message=f"{request.user.username} replied to your comment: '{comment.content}'"
                        )
                    )
            if notifications:
                Notification.objects.bulk_create(notifications)
                print('Notifications created')

            return Response({'message': 'Comment added successfully', 'comment': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        id = request.GET.get('id')
        if id:
            comment = Comment.objects.get(id=id)
            comment.delete()
            return Response({'message': 'Comment deleted successfully'}, status=status.HTTP_200_OK)
        return Response({'message': 'Invalid comment ID'}, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request):
        id = request.GET.get('id')
        if id:
            comment = Comment.objects.get(id=id)
            serializer = CommentCreateSerializer(comment)
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({'message': 'Invalid comment ID'}, status=status.HTTP_400_BAD_REQUEST)
    def patch(self, request):
        id = request.GET.get('id')
        if id:
            comment = Comment.objects.get(id=id)
            serializer = CommentCreateSerializer(comment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Comment updated successfully', 'comment': serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Invalid comment ID'}, status=status.HTTP_400_BAD_REQUEST)
    
class Recommanded(APIView):
    def get(self, request, dept, year):
        students = Student.objects.filter(department=dept, year=year).values_list('user', flat=True)
        post_filter = Post.objects.filter(user__in=students)
        posts = post_filter.order_by('-created_at')[:10]
        serializer = HomePostsSerializer(posts, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
    
class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    def list(self, request):
        queryset = self.get_queryset()
        data = []
        for notification in queryset:
            post_data = None
            if notification.comment and notification.comment.post:
                post_data = PostDetailSerializer(notification.comment.post).data
            data.append({
                "notification": NotificationSerializer(notification).data,
                "post": post_data
            })
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'])
    def mark_as_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({"message": "All notifications marked as read"}, status=200)
    
class UploadPost(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request):
        data = request.data
        print(data)
        serializer = UplaodPostSerializer(data=data) 
        if serializer.is_valid():
            print(serializer.validated_data)
            serializer.save(user=request.user)
            return Response({'message': 'Post uploaded successfully', 'post': serializer.data}, status=status.HTTP_201_CREATED)
    def get(self, request):
        serializer = UplaodPostSerializer(Post.objects.all(), many = True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        
class SavedPostView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def post(self, request):
        data = request.data
        serializer = SavedPostSerializer(data=data, context={'request': request}) 
        if serializer.is_valid():
            serializer.save(user=request.user, is_save = True)
            return Response({'message': 'Post saved successfully', 'saved_post': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        id = request.GET.get('id')
        if id:
            saved = SavedPost.objects.get(id = id)
            saved.delete()
            return Response({'message' : "saved post deleted successfully"})
    
    def get(self, request):
        user = request.GET.get('user')
        user_obj = User.objects.get(username = user)
        saved_posts = SavedPost.objects.filter(user=user_obj, is_save=True)
        serializer = DisplaySavedPostSerializer(saved_posts, many = True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
    
class ProfileView(APIView):
    def get(self, request):
        user = request.GET.get('user')
        user_obj = User.objects.get(username = user)
        serializer = ProfileSerializer(user_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        serializer = RegisterSerializer(data = data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message' : 'Register successfully', 'data' : serializer.validated_data}, status=status.HTTP_201_CREATED)
        return Response({'message':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class DisplayPostView(APIView):
    def get(self, request, pk):
        user_obj = User.objects.get(username = pk)
        post_objs = Post.objects.filter(user = user_obj)
        serializer = DisplayPosts(post_objs, many = True)
        return Response({'message' : 'successfully Retrived', "data" : serializer.data}, status=status.HTTP_200_OK)
    
    