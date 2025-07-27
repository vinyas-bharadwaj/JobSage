from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog_list, name='list'),
    path('create/', views.blog_create, name='create'),
    path('my-blogs/', views.my_blogs, name='my_blogs'),
    path('upload-image/', views.upload_image, name='upload_image'),
    path('<slug:slug>/edit/', views.blog_edit, name='edit'),
    path('<slug:slug>/delete/', views.blog_delete, name='delete'),
    path('<slug:slug>/', views.blog_detail, name='detail'),  # Move this to the end
]