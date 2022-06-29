
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
    list_display = ['id','title','slug', "created_at", "modified_at"] 
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

