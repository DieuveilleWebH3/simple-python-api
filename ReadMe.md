# Introduction #
 

This document provides the instructions for using / editing / interacting with the Simple Python API Application developed by ***Dieuveille BOUSSA ELLENGA***.   
**Simple Python API** is a well documented Python / Django-based Software (web service application or Application Programming Interface) for a blog (or blog-like) web application. 
The structure mimmick the one from the popular blog platform Medium but is limited to only BackEnd.
The APIs allows User Authentication with a multiple type users management (0: Publisher, 1: Author) and Blog's functionalities with several components.
Authors can add new categories, add new articles, request that their articles be published into one group (journal-like group) with other articles handled by a publisher, and much more.
Publishers can create groups, review the requests from authors to add their articles into groups or not, and much more.   
The APIs Application is based on the CRUD user interface convention, with restrictions depending on users' roles. 

<br />

![API - Swagger UI Panel ](/resources/api_swagger_.png)


<br />

# Document #

## Target audience ##

This document is targeted (but not limited) to technical individual with a Web Development background 

<br/>

#### The APIs are implemented in Python with the Django framework and PostgreSQL 

<br/>
<br/>

## Definition ##

### This is the **First Release** of the application or module. And so, many improvements must be done for future version / release 

    Code optimization : I used what is called as brute force method for most parts of the code, due to time constraint I had to write efficient code but not optimal so it is not necessary a very clean code  


About [Brute Force Method](http://catb.org/jargon/html/B/brute-force.html "Brute Force Method Description")

<br />
<br />

The API Module is based on the CRUD user interface convention.  

 - Create: 
    
        You can create new user instance, they can have different roles 
        Specific users (Publisher or Author) can add new categories, articles, groups, requests instances, ..
        Visitors (non user) can leave comments  


 - Read: 

        Users can access those blog instances, see the categories, articles, comments, …  
        Visitors (non user) can read articles  


 - Update:

        You can edit the blog instances, update categories, articles, groups, ...  


 - Delete: 
 
        You can also delete users, but it is advised not to, instead turn them inactive by unchecking the active field for that user on the Django Admin panel.  
        Users can delete blog instances, update categories, articles, groups, ...


<br />

# Application components #


## The database is comprised of 22 models, and they share relationships ... refer to **ER Diagram**


<br />

![API DataBase ER Diagram ](/resources/simple_python_api_erd.png)    

>> ER Diagram PostgreSQL  


<br />

### The main models (tables) are **Category**, **Articles**, **Users**, **Comments**, **PublishGroups**, **Demands** and **DemandsReviews**   


<br />

![API DataBase ER Diagram ](/resources/simple_python_api_class_diagram.png)    

>> Class Diagram  


<br />  
<br />

## Functions ##

<br />

### Simple Python API comprises a  
 - Authentication or Account module:

        Login Endpoint 

        Register Endpoint 

        Password Reset Endpoint

        User Profile Endpoint

    ![Authentication Endpoints](/resources/account_module_endpoints.png)

        


    ![Account Models](/resources/account_models.png)
 
 
- Blog Module:

        The normal user can add new complaints through a web portal 
        Which are saved, then analyzed and categorized through an api 
        



There are two ways to use the Account Module:  

Starting a fresh new project and integrating the module in it    

Using the module’s project as base and add other modules in it   

## 3.1 Starting New Project ##   

As a complementary module, the Account Module must be integrated in another project. 

**Attention** it is advised that this module be integrated before creating a user for your project, else, you will encounter a database migration issue (which you can still solve, but it is untoward)  

After starting a new project i.e. django-admin startproject mysite (mysite being the name of the project) we access the new directory mysite, and open the mysite folder  

We will modify two files, settings.py and urls.py, but first we copy the account module and the dashboard module to our main folder. 

We then open our IDE / text editor to edit the files. 


**In setting.py:**  mysite/settings.py  

In INSTALLED_APPS (~line 33) we comment the ‘django.contrib.admin’ line and we add two lines ‘account’, and ‘dashboard’, to register the two new apps to the project 

And we add AUTH_USER_MODEL = "account.User" after ALLOWED_HOSTS


**In urls.py:**  mysite/urls.py 

In urlpattern (~line 20) we comment the path(‘admin/’, admin.site.urls),  

And we also comment the from django.contrib import admin line  

Then, we run the migrations. 

After running the migrations, we create a superuser and we can uncomment everything we commented and run the migrations again.  

We now register the urls of our new apps, by importing include after path  

from django.urls import path, include  

and adding two new lines in urlpatterns   

path('account/', include('account.urls')), 

path('', include('dashboard.urls')), 


We add the static root, media root, template path in the settings.py and urls.py files. 
Then, we create one and only one instance of the allow_registration models from the django admin panel or using our terminal 


Cmd -> python ->  

import os 

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")  

from django.core.wsgi import get_wsgi_application 

application = get_wsgi_application() 

from account.models import *   

allow = AllowRegistration(name='user_registration', status=True)   

allow.save() 


Basics functionalities have been implemented: Login, Logout, Register, Edit Profile, Change Password, Reset or Recover Password. 

**Attention** the Registration view depends on the Admin, there is a functionality Allow_Registration which may (or may not) allow new users to register. 
The Admin must login and choose if people can register or not to the website, it can be changed on the dashboard or on the Django admin panel and it is set to True by default, meaning users can register to the web application.  


**In setting.py:** mysite/settings.py we add the following at the bottom of the page 

LOGIN_REDIRECT_URL = 'dashboard' 

LOGIN_URL = 'login' 

LOGOUT_URL = 'logout' 

LOGOUT_REDIRECT_URL = 'login' 

AUTHENTICATION_BACKENDS = [ 

    'django.contrib.auth.backends.ModelBackend', 

    'account.authentication.EmailAuthBackend' 

] 

This tells our application where to redirect the user after logging in and logging out and allows the users to also be able to login with their address email and password as well as username and password.  

And, so far, our project is up and running.  


## 3.2 Using Account Module as Base ## 

We clone the specific repository or download the compressed project; the project contains the Account module and the Dashboard module. 
The project has been dockerized (the docker-compose.yml may be changed according to the need of the project you are building), so we start by building the environment by running docker-compose build then docker-compose up  

This should also run the migrations, we can now create a super user and take a look at the app.  

By default, we have created 4 types of users: type1, type2, type3 and type4, the names can be changed in the models.py file (after every change, we must run the migrations, restarting docker works too).  

The Dashboard app has only one view redirected after we have logged in.

Basics functionalities have been implemented: Login, Logout, Register, Edit Profile, Change Password, Reset or Recover Password. 

**Attention** the Registration view depends on the Admin, there is a functionality Allow_Registration which may (or may not) allow new users to register. 
The Admin must login and choose if people can register or not to the website, it can be changed on the dashboard or on the Django admin panel and it is set to True by default, meaning users can register to the web application.  

The desired project can then be built around those modules and the different type of users can be given roles.



## 3.3 Email Server Configuration ## 

**In setting.py:** mysite/settings.py  

We need to configure the server to be able to send emails for the reset / recover password functionality.  

An example with gmail smtp server configuration  

We add at the bottom of settings.py  

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend" 

EMAIL_USE_TLS = True 

EMAIL_HOST = 'smtp.gmail.com' 

EMAIL_PORT = 587 

EMAIL_HOST_USER = 'john-doe@gmail.com' 

EMAIL_HOST_PASSWORD = 'JohnDoePassword' 

This uses the john doe gmail account to send emails to users wanting to recover their passwords (you have to modify the gmail settings to enable and allow less secure third app to use this feature) 

We can also test the functionality on our local server, by replacing (or commenting) all of the above by    

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' 

This will show the email in our terminal.

