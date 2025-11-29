from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('course/<path:course_id>/', views.course_detail, name='course_detail'),
    path('assignments/', views.assignments_view, name='assignments'),
    path('quizzes/', views.quizzes_view, name='quizzes'),
    path('grades/', views.grades_view, name='grades'),
    path('forums/', views.forums_view, name='forums'),
    path('ai-query/', views.ai_query_view, name='ai_query'),
]
