from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),          # Root / home page
    path('index/', views.index, name='index_alt'), # Just in case you access /index/
    path('book_ride/', views.book_ride, name='book_ride'),
    path('track-ride/<int:ride_id>/', views.track_ride, name='track_ride'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    # path('driver_dashboard/', views.driver_dashboard, name='driver_dashboard'),
    # path('dashboard/', views.user_dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('driver_register/', views.register_as_driver, name='driver_register'),
    path('update-location/', views.update_driver_location, name='update_location'),
    path('book-ride/', views.book_ride, name='book_ride'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('start-ride/<int:ride_id>/', views.start_ride, name='start_ride'),
    path('complete-ride/<int:ride_id>/', views.complete_ride, name='complete_ride'),
    path('submit-rating/<int:ride_id>/', views.submit_rating, name='submit_rating'),
    path('cancel-ride/<int:ride_id>/', views.cancel_ride, name='cancel_ride'),
    path('ride/<int:ride_id>/book-seat/', views.book_ride_seat, name='book_ride_seat'),
    path('ride/<int:ride_id>/accept/', views.accept_ride, name='accept_ride'),
    path('notifications/mark-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    # path('send-message/<int:user_id>/', views.send_user_message, name='send_user_message'),
    path('ride/<int:ride_id>/send-message/<int:user_id>/', views.send_user_message, name='send_user_message'),
    path('api/notifications/', views.fetch_notifications_api, name='fetch_notifications_api'),
    path('send-message/<int:ride_id>/<int:user_id>/', views.send_user_message, name='send_user_message_ride'),
    # path('send-message/<int:ride_id>/<int:user_id>/', views.send_user_message, name='send_user_message_ride'),
    path('live-location/', views.live_location_page, name='live_location_page'),
    
    
    
]