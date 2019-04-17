from django.contrib import admin
from django.urls import path
from . import views

app_name = 'customuser'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('user_create/', views.UserCreate.as_view(), name='user_create'),
    path('user_create/done', views.UserCreateDone.as_view(), name='user_create_done'),
    path('user_create/complete/<token>/', views.UserCreateComplete.as_view(), name='user_create_complete'),
    path('user_list/<str:get_username>', views.TestView.as_view(), name='test_userlist'),
    path('profile/<slug:get_name>', views.ProfileDetailView.as_view(), name='profile'),
    path('<slug:get_name>/follow', views.follow_view, name='follow'),
    path('<slug:get_name>/unfollow', views.unfollow_view, name='unfollow'),
]
