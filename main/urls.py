from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'main'
urlpatterns = [
    path('password_reset/', views.MainPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.MainPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('accounts/register/activate/<str:sign>/', views.user_activate, name='register_activate'),
    path('accounts/register/done/', views.RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/', views.RegisterUserView.as_view(), name='register'),
    path('accounts/profile/change/<int:pk>/', views.profile_bb_change, name='profile_bb_change'),
    path('accounts/profile/delete/<int:pk>/', views.profile_bb_delete, name='profile_bb_delete'),
    path('accounts/profile/change/', views.ChangeUserInfoView.as_view(), name='profile_change'),
    path('account/profile/delete/', views.DeleteUserView.as_view(), name='profile_delete'),
    path('accounts/profile/add/', views.profile_bb_add, name='profile_bb_add'),
    path('account/profile/<int:pk>/', views.profile_bb_detail, name='profile_bb_detail'),
    path('accounts/profile/', views.profile, name='profile'),
    path('accounts/password/change/', views.MainPasswordChangeView.as_view(), name='password_change'),
    path('accounts/logout/', views.MainLogoutView.as_view(), name='logout'),
    path('accounts/login/', views.MainLoginView.as_view(), name='login'),
    path('bbs/', views.bb_list, name='bb_list'),
    path('<int:rubric_pk>/<int:pk>/', views.detail, name='bb_detail'),
    path('<int:pk>/', views.by_rubric, name='by_rubric'),
    path('', views.index, name='index'),
]
urlpatterns += [
    path('<str:page>/', views.other_page, name='other'),
]
