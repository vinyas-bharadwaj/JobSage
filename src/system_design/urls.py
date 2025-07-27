# system_design/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.system_design_page, name='system-design-page'),
    path('question/<int:question_id>/', views.design_question_view, name='design-question'),
    path('question/<int:question_id>/submit/', views.submit_design_view, name='submit-design'),
    path('results/<int:submission_id>/', views.design_results_view, name='design-results'),
    path('my-submissions/', views.user_submissions_view, name='user-submissions'),
]