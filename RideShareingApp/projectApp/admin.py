from django.contrib import admin
from .models import UserProfile, DriverProfile, Ride, RideBooking

# Register your models here.
# admin.site.register(UserProfile)
# admin.site.register(DriverProfile)
# admin.site.register(Ride)
# admin.site.register(RideBooking)

class DriverProfileInline(admin.StackedInline):
    model = DriverProfile
    can_delete = False
    verbose_name_plural = 'Driver Profile Details'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email', 'role', 'phone_number')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'phone_number')
    
    # This adds the User model fields to the edit form view
    readonly_fields = ('get_username', 'get_email', 'get_first_name', 'get_last_name')
    
    # Organize how they appear on the page
    fields = ('get_username', 'get_email', 'get_first_name', 'get_last_name', 'user', 'profile_picture', 'phone_number', 'bio', 'role')
    
    inlines = [DriverProfileInline]

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email Address'

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Last Name'    



from .models import Rating

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'ride', 'given_by', 'given_to', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('given_by__username', 'given_to__username', 'comment')

@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'cnic_number', 'vehicle_model', 'vehicle_plate', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('user_profile__user__username', 'cnic_number', 'vehicle_plate')

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ('id', 'passenger', 'pickup_address', 'dropoff_address', 'fare', 'status', 'created_at')
    list_filter = ('status', 'created_at')

@admin.register(RideBooking)
class RideBookingAdmin(admin.ModelAdmin):
    list_display = ('ride', 'passenger', 'seats_booked', 'booked_at')