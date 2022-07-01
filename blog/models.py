
"""

    Created on Tuesday, June 28 2022  11:26:54 
    
    @author: Dieuveille BOUSSA ELLENGA
    
"""


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
    description = models.CharField(max_length=300, null=True, blank=True, default="")

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
    
    read_by = models.IntegerField(default=0)
    liked_by = models.IntegerField(default=0)
    
    photo = models.ImageField(upload_to="article_photos", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{str(self.slug)} - {str(self.author.username)} - {str(self.read_by)}'


# Model PublishGroups  
class PublishGroups(models.Model):
    
    publisher = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    articles = models.ManyToManyField(Articles, blank=True, related_name='group_articles')

    title = models.CharField(max_length=255, unique=True, blank=False, null=False)
    slug = models.CharField(max_length=255, unique=True)
    
    description = models.TextField(null=True, blank=True)
    
    photo = models.ImageField(upload_to="group_photos", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{str(self.slug)} - {str(self.publisher.username)} - {str(self.description)}'


# Model Comments  
class Comments(models.Model):
    
    article = models.ForeignKey(Articles, blank=True, null=True, on_delete=models.SET_NULL)
    
    name = models.CharField(max_length=255, unique=False, blank=False, null=False)
    
    content = models.TextField(null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{str(self.article.slug)} - {str(self.name)}'



# Model Demands  
class Demands(models.Model):
    
    author = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    publish_group = models.ForeignKey(PublishGroups, blank=False, null=False, on_delete=models.CASCADE)

    article = models.ForeignKey(Articles, blank=False, null=False, on_delete=models.CASCADE)

    content = models.TextField(null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{str(self.author.username)} - {str(self.publish_group.slug)} - {str(self.article.slug)}'



# Model DemandsReviews  
class DemandsReviews(models.Model):
    
    publisher = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    demand = models.ForeignKey(Demands, blank=False, null=False, on_delete=models.CASCADE)

    content = models.TextField(null=False, blank=False)
    
    status = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{str(self.publisher.username)} - {str(self.demand.id)} - {str(self.status)}'

