from django.urls import path
from . import views  # Assuming your views are in the same directory

#Urls.py, all work is done on same page so there are no redirects
urlpatterns = [
    path('', views.autocomplete, name='autocomplete'),
    path('remove-filter/', views.remove_filter, name='remove_filter'),
    path('download/', views.download_data, name='download_data'),
]