from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.


class CustomSignupForm(UserCreationForm):
    email = forms.EmailField(required=False, help_text="Optional email address.")
    profile_picture = forms.ImageField(required=False, help_text="Optional profile picture.")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        user = super().save(commit=commit)
        user.email = self.cleaned_data.get('email', '')
        if commit:
            user.save()
            # Handle profile picture saving if using a UserProfile model
            profile_pic = self.cleaned_data.get('profile_picture')
            if profile_pic:
                # Assuming UserProfile exists
                from .models import UserProfile
                UserProfile.objects.create(User=user, profile_image=profile_pic)
        return   user
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    USER_ROLES = (
        ('passenger', 'Passenger'),
        ('driver', 'Driver'),
    )
    role = models.CharField(max_length=20, choices=USER_ROLES, default='passenger')

    def __str__(self):
        return f"{self.user.username} - {self.role}"



from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    ride = models.ForeignKey('Ride', on_delete=models.SET_NULL, null=True, blank=True, related_name='ride_notifications') # Changed Ride to 'Ride'
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"

class DriverProfile(models.Model):
    # Linked to UserProfile instead of duplicating user/phone details
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='driver_details')
    
    # CNIC Details
    cnic_number = models.CharField(max_length=15, unique=True, help_text="Enter your 13-digit CNIC number")
    cnic_front_doc = models.FileField(upload_to='driver_documents/cnic/', help_text="Upload CNIC Front Side")
    cnic_back_doc = models.FileField(upload_to='driver_documents/cnic/', help_text="Upload CNIC Back Side")
    
    pickup_lat = models.FloatField(null=True, blank=True)
    pickup_lng = models.FloatField(null=True, blank=True)
    dropoff_lat = models.FloatField(null=True, blank=True)
    dropoff_lng = models.FloatField(null=True, blank=True)
    
    # Vehicle Details
    license_number = models.CharField(max_length=50)
    vehicle_model = models.CharField(max_length=100)
    vehicle_plate = models.CharField(max_length=20)
    
    # Vehicle Document uploads
    drivers_license_doc = models.FileField(upload_to='driver_documents/licenses/', help_text="Upload Driver's License")
    vehicle_registration_doc = models.FileField(upload_to='driver_documents/vehicles/', help_text="Upload Vehicle Registration")
    
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Driver: {self.user_profile.user.username} ({self.cnic_number})"
    
    
class Ride(models.Model):
    STATUS_CHOICES = (
        ('requested', 'Requested'),
        ('accepted', 'Accepted'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rides_as_passenger')
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='rides_as_driver')
    
    # Locations
    pickup_address = models.CharField(max_length=255)
    pickup_lat = models.FloatField()
    pickup_lng = models.FloatField()
    
    dropoff_address = models.CharField(max_length=255)
    dropoff_lat = models.FloatField()
    dropoff_lng = models.FloatField()
    
    # Fare and Seats Sharing
    fare = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    original_fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fare_verified_by_passenger = models.BooleanField(default=True)
    total_seats = models.PositiveIntegerField(default=4)  # e.g., Car has 4 seats
    booked_seats = models.PositiveIntegerField(default=1) # Seats booked by current passenger(s)
    
    # Live driver coordinates
    current_lat = models.FloatField(null=True, blank=True)
    current_lng = models.FloatField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    created_at = models.DateTimeField(auto_now_add=True)
    
    scheduled_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='requested')
    
    total_seats = models.IntegerField(default=4)
    booked_seats = models.IntegerField(default=0)

    @property
    def remaining_seats(self):
        return max(0, self.total_seats - self.booked_seats)

    def __str__(self):
        return f"Ride #{self.id} - {self.dropoff_address} ({self.booked_seats}/{self.total_seats} seats)"

class RideBooking(models.Model):
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='bookings')
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ride_bookings')
    seats_booked = models.PositiveIntegerField(default=1)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.passenger.username} booked {self.seats_booked} seat(s) on Ride #{self.ride.id}"
    
    
    
class Rating(models.Model):
    ride = models.ForeignKey('Ride', on_delete=models.CASCADE, related_name='ratings')
    given_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    given_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_ratings')
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating score from 1 to 5 stars"
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensures a user can only rate a specific ride partner once per ride
        unique_together = ('ride', 'given_by', 'given_to')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.given_by.username} rated {self.given_to.username} - {self.score}★ (Ride #{self.ride.id})"