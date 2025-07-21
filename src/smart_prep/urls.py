from django.urls import path
from . import views

urlpatterns = [
    path('', views.smart_prep_page, name='smart-prep'),
    path('create/', views.create_prep_session, name='create-prep-session'),
    path('session/<str:session_id>/', views.prep_session_detail, name='prep-session-detail'),
]