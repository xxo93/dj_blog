# from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter

from . import views
# 定义视图集的路由
router = DefaultRouter()
# router.register('books', views.test)    # 视图类


urlpatterns = [
    path('test', views.test),
]

# 将试图集的路由添加到urlpattens
urlpatterns += router.urls