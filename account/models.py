
"""

    Created on Monday, June 27 2022  15:37:54 
    
    @author: Dieuveille BOUSSA ELLENGA
    
"""


from django.db import models 
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
import os


# Create your models here.


# Model Users 
class User(AbstractUser):
    
    ACCOUNT_TYPE_CHOICES = ( 
        ('0', 'Publisher'), 
        ('1',  'Author'),
    ) 
    
    def get_upload_path(self, filename):
        
        return 'users/{0}/{1}'.format(self.username, filename)
    
    email = models.EmailField(unique=True)

    user_type = models.CharField(max_length=50, choices=ACCOUNT_TYPE_CHOICES, default='1')

    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to=get_upload_path, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

