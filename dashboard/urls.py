
"""

    Created on Monday, June 21 2022  12:57:54 
    
    @author: Dieuveille BOUSSA ELLENGA
    
"""


from django.urls import path, include
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [

    # 
    path('', views.index, name='index'),
    
]
