
"""

    Created on Tuesday, June 28 2022  11:26:54 
    
    @author: Dieuveille BOUSSA ELLENGA
    
"""


from django.db import models 
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
import os


# Create your models here.

# Model Axe 
class Category(models.Model):
    title = models.CharField(max_length=255, unique=True, blank=False, null=False)
    slug = models.CharField(max_length=255, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
        
    def __str__(self):
        return self.title


# Model Theme 
class Theme(models.Model):
    axe = models.ForeignKey(Axe, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, unique=False, blank=False, null=False)
    slug = models.CharField(max_length=255, unique=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
        
    def __str__(self):
        return f'{str(self.title)} - {str(self.axe)}'




