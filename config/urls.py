from django.contrib import admin
from django.urls import path

from tester.views import start_load_test

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', start_load_test, name='start_load_test'),
]
