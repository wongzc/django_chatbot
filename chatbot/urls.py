from django.urls import path
from . import views
urlpatterns =[
    path('', views.chatbot, name='chatbot'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('clear/<str:pk>', views.clear, name='clear'),

    path('changemodel', views.changemodel, name='changemodel'),
]