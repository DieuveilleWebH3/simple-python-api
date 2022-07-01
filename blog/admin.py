
"""

    Created on Tuesday, June 28 2022  11:26:54 
    
    @author: Dieuveille BOUSSA ELLENGA
    
"""

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *


# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)} 
    list_display = ['id','title','slug', "description", "created_at", "modified_at"] 
    search_fields = ['title', 'id' ] 
    filter_fields = ['title', 'slug'] 


@admin.register(Articles)
class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)} 
    list_display = ['id','title','slug', 'author', 'categories', "created_at", "modified_at"] 
    search_fields = ['title', 'id' ] 
    filter_fields = ['author',]
    
    def categories(self, obj): 
        return "\n \n".join([f'{t.title} , ' for t in obj.category.all()]) 


@admin.register(Comments)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id','name','article', 'content', "created_at", "modified_at"] 
    search_fields = ['name', 'content', 'article__content' ] 
    filter_fields = ['name', 'article']


@admin.register(PublishGroups)
class PublishGroupsAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)} 
    list_display = ['id','publisher','articles', 'title', 'slug', 'description', "created_at", "modified_at"] 
    search_fields = ['title', 'description' ] 
    filter_fields = ['publisher']
    
    def articles(self, obj): 
        return "\n \n".join([f'{t.title} , ' for t in obj.articles.all()]) 


@admin.register(Demands)
class DemandsAdmin(admin.ModelAdmin): 
    list_display = ['id','author','article', 'publish_group', 'content', "created_at", "modified_at"] 
    search_fields = ['article__title', 'publish_group__title' ] 
    filter_fields = ['publish_group', 'article', 'author']
    
    

