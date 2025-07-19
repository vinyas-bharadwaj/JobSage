from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login-page'),
    path('signup/', views.signup_view, name='signup-page'),
    path('logout/', views.logout_view, name='logout-page'),
]