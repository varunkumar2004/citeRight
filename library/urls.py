from django.urls import path
from . import views

urlpatterns = [
    path('', views.paper_list, name='paper-list'),
    path('uplaod/', views.upload_paper, name='upload_paper'),
    path('paper/<int:pk>/', views.paper_detail, name='paper_detail'),
]