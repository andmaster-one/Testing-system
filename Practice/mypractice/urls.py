import debug_toolbar
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', include('testing.urls', namespace='testing-service')),
    path('accounts/', include('allauth.urls')), 
    path('admin/', admin.site.urls),

]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls)),]



