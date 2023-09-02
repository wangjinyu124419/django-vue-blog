from django.urls import path, include
from rest_framework import routers

from . import views
from .views import HaystackSearchView, ArticleViewSet

app_name = 'article'
# todo 同时处理结尾反斜线匹配

urlpatterns = [
    # path('', include(router.urls)),
    # path('detail/<int:article_id>/', views.old_detail, name='old_detail'),
    # path('detail/<int:article_id>/<str:slug>', views.re_detail, name='re_detail'),
    path('<int:article_id>/<str:slug>', views.slug_detail, name='slug_detail'),
    # path('<int:article_id>', views.detail, name='detail'),
    # path('update/<int:article_id>', views.update, name='update'),
    # path('create', views.create, name='create'),
    # path('upload/image', views.upload, name='upload'),
    # path('search', HaystackSearchView(), name='haystack_search'),

]
