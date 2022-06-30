from django.urls import path, include, re_path
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from requests import put

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views import defaults as default_views


from .views import *

from rest_framework import permissions, routers
from rest_framework.routers import DefaultRouter, SimpleRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework.documentation import include_docs_urls
from rest_framework_swagger.views import get_swagger_view

router = DefaultRouter() if settings.DEBUG else SimpleRouter()


schema_view = get_schema_view(
    openapi.Info(
        title="Simple Python API",
        default_version='v2',
        description="Simple Python API, web services",
        terms_of_service="https://www.ourapp.com/policies/terms/",
        contact=openapi.Contact(email="d.boussaellenga@h3hitema.fr"),
        license=openapi.License(name="Dieuveille BOUSSA ELLENGA License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# schema_view = get_swagger_view(title="Swagger Docs")

urlpatterns = [
    re_path(r'^doc(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),  #<-- Here

    path('doc/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),  #<-- Here
         
    
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # url(r'^docs/', schema_view),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),


    path("openid/", include("oidc_provider.urls", namespace="oidc_provider")),

    path('admin/doc/', include('django.contrib.admindocs.urls')),

    
    path('login/', LoginAPIView.as_view(), name="api_login"),
    path('register/', RegisterView.as_view(), name="api_register"),


    # path('request-reset-email/', RequestPasswordResetEmail.as_view(), name="request-reset-email"),
    # path('password-reset/<uidb64>/<token>/', PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    # path('password-reset-complete', SetNewPasswordAPIView.as_view(), name='password-reset-complete'),
    
    
    # 
    path('category/', CategoryViewSet.as_view({'get': 'list', 'post':'create'}), name="category"), 
    path('category/<slug>', CategoryViewSet.as_view({'put': 'update'}), name='category'),
    
    # 
    path('articles/', ArticleViewSet.as_view({'get': 'list', 'post':'create'}), name="articles"), 
    path('articles/<slug>', ArticleViewSet.as_view({'put': 'update', 'delete':'delete'}), name='articles'),
    
    # path('articles/<user_id>', ArticleViewSet.as_view({'get': 'user_articles'}), name='articles'),
    
    # 
    path('comments/', CommentsViewSet.as_view({'get': 'list', 'post':'create'}), name="comments"), 
    # path('comments/<article_slug>', CommentsViewSet.as_view({'get': 'list'}), name='comments'),
    
    
]


urlpatterns += router.urls


"""
if settings.DEBUG:
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
"""
