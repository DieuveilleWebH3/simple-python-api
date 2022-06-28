
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

