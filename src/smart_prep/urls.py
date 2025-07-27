from django.urls import path
from . import views

urlpatterns = [
    path('', views.smart_prep_page, name='smart-prep'),
    path('session/<str:session_id>/', views.prep_session_detail, name='prep-session-detail'),
]