from django.urls import path
from . import views


app_name = 'profiles'

urlpatterns = [
    path('<str:username>/', views.profile_view, name='profile_view'),
    
    # Routes for the follow/unfollow functionality
    path('<str:username>/follow/', views.follow_user, name='follow_user'),
    path('<str:username>/unfollow/', views.unfollow_user, name='unfollow_user'),
]
