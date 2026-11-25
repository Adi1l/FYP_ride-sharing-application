"""
URL configuration for RideShareing project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django import views
from django.contrib import admin
from django.urls import path
from django.urls import include
from projectApp.views import  cancel_ride, complete_ride, user_dashboard, login, signup, index, profile_view, register_as_driver, update_driver_location, get_driver_location, accept_ride, update_ride_status, book_ride, track_ride, start_ride, submit_rating
from RideShareing.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("projectApp.urls")),
    # path('driver_dashboard/', driver_dashboard, name='driver_dashboard'),
    path('dashboard/', user_dashboard, name='dashboard'),
    path('cancel-ride/<int:ride_id>/', cancel_ride, name='cancel_ride'),
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('', index, name='index'),          # Root / home page
    path('index/', index, name='index_alt'), # Just in case you access /index/
    path('book_ride/', book_ride, name='book_ride'),
    path('track-ride/<int:ride_id>/', track_ride, name='track_ride'),
    path('profile/', profile_view, name='profile'),
    path('driver_register/', register_as_driver, name='driver_register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('update-location/', update_driver_location, name='update_location'),
    path('get-driver-location/<int:ride_id>/', get_driver_location, name='get_driver_location'),
    # path('driver/dashboard/', driver_dashboard, name='driver_dashboard'),
    path('driver/accept-ride/<int:ride_id>/', accept_ride, name='accept_ride'),
    path('driver/update-status/<int:ride_id>/<str:new_status>/', update_ride_status, name='update_ride_status'),
    path('book-ride/', book_ride, name='book_ride'),
    path('start-ride/<int:ride_id>/', start_ride, name='start_ride'),
    path('complete-ride/<int:ride_id>/', complete_ride, name='complete_ride'),
    path('submit-rating/<int:ride_id>/', submit_rating, name='submit_rating'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)