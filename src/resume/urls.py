from django.urls import path
from . import views

urlpatterns = [
   path('', views.resume_page, name="resume-page")
]
