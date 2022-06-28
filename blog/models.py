
"""

    Created on Tuesday, June 28 2022  11:26:54 
    
    @author: Dieuveille BOUSSA ELLENGA
    
"""


import imp
from django.db import models 
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group

from account.models import *

import os


# Create your models here.

# Model Category 
class Category(models.Model):
    title = models.CharField(max_length=255, unique=True, blank=False, null=False)
    slug = models.CharField(max_length=255, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
        
    def __str__(self):
        return self.title


# Model Articles  
class Articles(models.Model):
    
    author = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    category = models.ManyToManyField(Category, blank=True, related_name='articles_category')

    title = models.CharField(max_length=255, unique=True, blank=False, null=False)
    slug = models.CharField(max_length=255, unique=True)
    content = models.TextField(null=True, blank=True)
    
    read_by = models.IntegerField()
    liked_by = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{str(self.slug)} - {str(self.author.username)} - {str(self.read_by)}'
    

