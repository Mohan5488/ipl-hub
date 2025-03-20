from django.urls import path,include
from posts.views import LoginView, DashboardViewSet, CategoryFeedView, PostView, AddCommentView, Recommanded, NotificationViewSet, UploadPost, SavedPostView, ProfileView, RegisterView,DisplayPostView, ChangePasswordView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('post-view', PostView, basename='post-view')
router.register('notifications', NotificationViewSet, basename='notifications')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view()),
    path('dashboard/', DashboardViewSet.as_view()),
    path('feed/<str:dept>/<int:year>/<int:category>/', CategoryFeedView.as_view()),
    path('add-comment/', AddCommentView.as_view(), name='add-comment'),
    path('recommend/<str:dept>/<int:year>/', Recommanded.as_view()),
    path('upload-post/', UploadPost.as_view()),
    path('saved/', SavedPostView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('register/', RegisterView.as_view()),
    path('display/<str:pk>/',DisplayPostView.as_view()),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]