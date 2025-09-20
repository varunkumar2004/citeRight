from django.urls import path
from . import views

# app_name helps Django distinguish between URL names from different apps
app_name = 'papers'

urlpatterns = [
    path('', views.paper_list_view, name='paper_list'), # This pattern handles the universal list of all papers (e.g., your homepage)
    path('profile/<str:username>/', views.paper_list_view, name='profile_view'), # This pattern handles the user-specific profile page
    path('paper/<int:pk>/', views.paper_detail, name='paper_detail'), # This pattern handles the detail view for a single paper
    path('upload/', views.upload_paper, name='upload_paper'), # This pattern handles the paper upload page    
    path('delete/<int:pk>', views.delete_paper, name='delete_paper'), # This pattern handles the paper upload page
]

