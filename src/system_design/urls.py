from django.urls import path
from . import views

urlpatterns = [
    path('', views.system_design_page, name='system-design-page'),
    path('analyze/', views.analyze_system_design_view, name='analyze-system-design'),
]