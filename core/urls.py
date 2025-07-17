from django.urls import path
from . import views

urlpatterns = [
    path('', views.signup_view, name='signup'),
    path('rules/', views.rules_view, name='rules'),
    path('assessment/', views.assessment_view, name='assessment'),
    path('submit/', views.submit_view, name='submit'),
    path('test-ended/', views.test_ended_view, name='test_ended'),
    path('review/', views.review_view, name='review'), 
    path('final-submit/', views.final_submit_view, name='final_submit'),
]