from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('quoter.urls'))
]

from quoter.views import page_not_found
handler404 = page_not_found

