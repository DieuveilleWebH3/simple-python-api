
"""

    Created on Monday, June 21 2022  12:57:54 
    
    @author: Dieuveille BOUSSA ELLENGA
    
"""

from unittest import result
from django.shortcuts import render, get_object_or_404, redirect, reverse

from django.core.files.storage import FileSystemStorage

from django.core import mail
from django.core.mail import EmailMessage, EmailMultiAlternatives

from django import template

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text, smart_bytes, smart_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.html import strip_tags
from django.template.loader import render_to_string 

import os
import re
import requests
import datetime
from datetime import *
from time import perf_counter, sleep
import json
from json import dumps, loads, JSONEncoder, JSONDecoder
import random
import csv
import xlrd
import openpyxl

# from account.forms import *
# from account.models import *
from .models import *
from simple_python_api.settings import MEDIA_ROOT, BASE_DIR

# Create your views here.


def index(request):
    
    # we request the user
    # user = request.user


    context = {
        # 'user': user,
        }
        
    return render(request, 'dashboard/index.html', context)

