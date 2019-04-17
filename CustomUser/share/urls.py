"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'share'

urlpatterns = [
    path('', views.CategoryIndexView.as_view(), name='index'),
    path('detail/<str:get_name>/', views.UrlIndexView.as_view(), name='index_url'),
    path('create/url', views.UrlCreateView.as_view(), name='create_url'),
    path('create/category/', views.CategoryCreateView.as_view(), name='create_category'),
    path('delete_url/', views.Urldelete, name='delete_url'),
    path('delete_subclass/', views.Categorydelete, name='delete_category'),
    path('admin/', admin.site.urls),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""
