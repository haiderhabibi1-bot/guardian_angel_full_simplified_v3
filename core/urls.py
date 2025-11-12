
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('public-questions/', views.public_questions, name='public_questions'),
    path('ask-public-question/', views.ask_public_question, name='ask_public_question'),
    path('lawyers/', views.lawyers_list, name='lawyers_list'),

    path('register/', views.register_customer, name='register'),
    path('register-lawyer/', views.register_lawyer, name='register_lawyer'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('settings/', views.settings_customer, name='settings_customer'),
    path('settings-lawyer/', views.settings_lawyer, name='settings_lawyer'),
    path('about/', views.about, name='about'),
    path('switch-language/', views.switch_language, name='switch_language'),

    path('answer/<int:pk>/', views.answer_question, name='answer_question'),
]
