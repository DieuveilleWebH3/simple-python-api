
"""

    Created on Monday, June 27 2022  15:37:54 
    
    @author: Dieuveille BOUSSA ELLENGA
    
"""


from django.urls import path, include
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [

    # register view
    path('test/', views.test, name='test'),

    # register view
    path('register/', views.register, name='register'),

    # we add the URL for the activate view, to allow users to activate their account.
    # url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate, name='activate'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    #  login view
    path('login/', views.user_login, name='login'),
    # path('login/', auth_views.LoginView.as_view(), name='login'),

    # we add the URL for the profile view, to allow users to see their personal info.
    path('profile', views.profile, name="profile"),

    # we add the URL for the edit view, to allow a user to edit / update their personal info.
    path('edit/', views.edit, name='edit'),

    # we add the URL for the change_password view, to allow a user to change their password.
    path('change_password', views.change_password, name="change_password"),

    # 
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # change password urls
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    # reset password urls
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='account/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='account/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='account/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='account/password_reset_complete.html'), name='password_reset_complete'),

    # alternative way to include authentication views
    path('', include('django.contrib.auth.urls')),
]
