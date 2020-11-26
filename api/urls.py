from django.urls import path

from . import views


urlpatterns = [
    path('bbs/<int:pk>/comments/', views.comments),
    path('bbs/<int:pk>/', views.BbDetailView.as_view()),
    path('bbs/', views.bbs),
]
