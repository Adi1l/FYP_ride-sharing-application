from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import UserProfile, DriverProfile, Ride, RideBooking
from .models import UserProfile
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth.forms import PasswordChangeForm
from .models import DriverProfile
from .forms import DriverRegistrationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, DriverProfile
import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Ride, RideBooking
from django.shortcuts import render
from .models import Ride

def index(request):
    rides = Ride.objects.all().distinct().order_by('-created_at')

    # 1. Status Filter
    status = request.GET.get('status')
    if status:
        rides = rides.filter(status=status).distinct()

    # 2. Destination Search
    destination = request.GET.get('destination')
    if destination:
        rides = rides.filter(dropoff_address__icontains=destination).distinct()
        
    # 3. Budget Filter
    budget = request.GET.get('budget')
    if budget:
        try:
            max_budget = float(budget)
            rides = rides.filter(fare__lte=max_budget).distinct()
        except ValueError:
            pass

    return render(request, 'index.html', {'rides': rides})

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # form.get_user() automatically authenticates and returns the user
            user = form.get_user()
            
            # Use the imported auth_login function safely without naming conflicts
            auth_login(request, user)
            
            return redirect('index') # or your success URL
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'login.html', {'form': form})
    
from .forms import SignUpForm
from django.contrib.auth.models import User
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Extract basic user info
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            password = form.cleaned_data.get('password')
            phone_number = form.cleaned_data.get('phone_number')

            # Create User object securely
            user = User.objects.create_user(
                username=username, 
                email=email, 
                password=password, 
                first_name=first_name, 
                last_name=last_name
            )
            
            # Create or update associated UserProfile with phone number
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.phone_number = phone_number
            profile.save()

            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})

@login_required
def profile_view(request):
    # Ensure profile object exists
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Check which action/form was submitted
        if 'update_profile' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
            
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('profile')
            else:
                messages.error(request, 'Please correct the errors below.')

        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Prevent user from being logged out
                messages.success(request, 'Your password was successfully updated!')
                return redirect('profile')
            else:
                messages.error(request, 'Please correct the password errors below.')

        elif 'delete_account' in request.POST:
            user = request.user
            logout(request)
            user.delete()
            messages.success(request, 'Your account has been permanently deleted.')
            return redirect('index')

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
        password_form = PasswordChangeForm(request.user)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'profile': profile,
    }
    return render(request, 'profile.html', context)


@login_required
def register_as_driver(request):
    # Get or create the user profile for the current user
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Automatically check if this logged-in user's profile already has a driver profile
    existing_driver = DriverProfile.objects.filter(user_profile=user_profile).first()
    if existing_driver:
        messages.info(request, "You are already registered as a driver.")
        return redirect('dashboard') # Updated to point to your unified dashboard

    if request.method == 'POST':
        form = DriverRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            driver = form.save(commit=False)
            driver.user_profile = user_profile  # Automatically links current user's profile
            driver.save()
            
            # Update user role to driver
            user_profile.role = 'driver'
            user_profile.save()
            
            messages.success(request, 'Your driver profile and CNIC documents have been successfully submitted!')
            return redirect('dashboard') # Updated to your unified dashboard URL name
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DriverRegistrationForm()

    return render(request, 'driver_register.html', {'form': form})


@login_required
def update_driver_location(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ride_id = data.get('ride_id')
            lat = data.get('lat')
            lng = data.get('lng')

            # Update the ride with the driver's current coordinates
            ride = Ride.objects.get(id=ride_id, driver=request.user)
            ride.current_lat = lat
            ride.current_lng = lng
            ride.save()

            return JsonResponse({'status': 'success', 'message': 'Location updated successfully.'})
        except Ride.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Ride not found or unauthorized.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@login_required
def get_driver_location(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)
    return JsonResponse({
        'driver_lat': ride.driver_lat,
        'driver_lng': ride.driver_lng,
        'pickup_lat': ride.pickup_lat,
        'pickup_lng': ride.pickup_lng,
        'dropoff_lat': ride.dropoff_lat,
        'dropoff_lng': ride.dropoff_lng,
        'status': ride.status
    })
        
@login_required(login_url='login')
def cancel_ride(request, ride_id):
    # Retrieve the ride by ID
    ride = get_object_or_404(Ride, id=ride_id)

    # If the creator (main passenger) cancels the ride
    if ride.passenger == request.user:
        ride.status = 'canceled'
        ride.save()
        messages.success(request, f"Ride #{ride.id} has been canceled.")
    
    # If a joined passenger cancels their seat booking
    elif RideBooking.objects.filter(ride=ride, passenger=request.user).exists():
        booking = RideBooking.objects.filter(ride=ride, passenger=request.user)
        booking.delete()
        messages.info(request, f"Your booking for Ride #{ride.id} has been canceled.")
    
    # If the driver cancels/rejects the ride assignment
    elif ride.driver == request.user:
        ride.driver = None
        ride.status = 'requested'
        ride.save()
        messages.warning(request, f"You dropped Ride #{ride.id}. It is back in requested status.")
    else:
        messages.error(request, "You do not have permission to cancel this ride.")

    return redirect('dashboard')


from django.db.models import Q, Avg
@login_required(login_url='login')
def user_dashboard(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # 1. Get IDs of rides booked/joined by the user as a passenger
    booked_ride_ids = RideBooking.objects.filter(passenger=request.user).values_list('ride_id', flat=True)

    # 2. Get all rides created by user, booked by user, OR accepted/driven by user
    user_all_rides = Ride.objects.filter(
        Q(passenger=request.user) | Q(id__in=booked_ride_ids) | Q(driver=request.user)
    ).distinct()

    # 3. Filter active rides (excluding completed and canceled ones)
    active_rides = user_all_rides.exclude(
        status__in=['completed', 'canceled']
    ).order_by('-id')

    # 4. Filter ride history
    ride_history = user_all_rides.filter(
        status__in=['completed', 'canceled']
    ).order_by('-id')

    # Counters
    total_rides = user_all_rides.count()
    completed_rides = user_all_rides.filter(status='completed').count()
    canceled_rides = user_all_rides.filter(status='canceled').count()
    ongoing_rides = active_rides.count()

    # 5. Calculate Actual Passenger Rating (Ratings received by request.user)
    passenger_avg = Rating.objects.filter(given_to=request.user).aggregate(Avg('score'))['score__avg']
    user_rating = round(passenger_avg, 1) if passenger_avg else 0.0

    # 6. Calculate Actual Driver Rating
    driver_rating = 0.0
    if profile.role == 'driver' or DriverProfile.objects.filter(user_profile=profile).exists():
        driver_avg = Rating.objects.filter(given_to=request.user).aggregate(Avg('score'))['score__avg']
        driver_rating = round(driver_avg, 1) if driver_avg else 0.0

    context = {
        'profile': profile,
        'total_rides': total_rides,
        'completed_rides': completed_rides,
        'canceled_rides': canceled_rides,
        'ongoing_rides': ongoing_rides,
        'user_rating': user_rating,
        'driver_rating': driver_rating,
        'active_rides': active_rides,
        'ride_history': ride_history,
        'notifications': [],
    }
    return render(request, 'dashboard.html', context)

@login_required
def accept_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id, status='requested')
    ride.driver = request.user
    ride.status = 'accepted'
    ride.save()
    messages.success(request, f"You have accepted Ride #{ride.id}.")
    return redirect('driver_dashboard')

@login_required
def update_ride_status(request, ride_id, new_status):
    ride = get_object_or_404(Ride, id=ride_id, driver=request.user)
    if new_status in ['ongoing', 'completed', 'cancelled']:
        ride.status = new_status
        ride.save()
        messages.success(request, f"Ride status updated to {new_status}.")
    return redirect('driver_dashboard')


import math
def calculate_distance_km(lat1, lon1, lat2, lon2):
    """Calculate distance in kilometers between two GPS coordinates using Haversine formula."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon1 - lon2)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@login_required
def book_ride(request):
    if request.method == 'POST':
        pickup_address = request.POST.get('pickup_address')
        
        # Fallback to default Multan coordinates if fields are empty
        pickup_lat = request.POST.get('pickup_lat')
        pickup_lat = float(pickup_lat) if pickup_lat else 30.1575
        
        pickup_lng = request.POST.get('pickup_lng')
        pickup_lng = float(pickup_lng) if pickup_lng else 71.5249
        
        dropoff_address = request.POST.get('dropoff_address')
        
        dropoff_lat = request.POST.get('dropoff_lat')
        dropoff_lat = float(dropoff_lat) if dropoff_lat else 30.1650
        
        dropoff_lng = request.POST.get('dropoff_lng')
        dropoff_lng = float(dropoff_lng) if dropoff_lng else 71.4934
        
        raw_fare = request.POST.get('fare')
        
        raw_seats = request.POST.get('total_seats') or request.POST.get('seats', 1)
        requested_seats = int(raw_seats) if raw_seats else 1
        
        scheduled_time = request.POST.get('scheduled_time')
        status = 'scheduled' if scheduled_time else 'requested'

        # --- AUTOMATIC FARE CALCULATION IN PKR ---
        if raw_fare and float(raw_fare) > 0:
            fare = float(raw_fare)
        else:
            # Calculate distance in kilometers using coordinates
            distance_km = calculate_distance_km(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng)
            
            # Realistic Pakistani pricing: Base Fare (150 PKR) + Per KM Rate (75 PKR/km)
            base_fare = 150.00
            per_km_rate = 75.00
            
            calculated_fare = base_fare + (distance_km * per_km_rate)
            fare = round(calculated_fare, 2)

        # Create the ride instance with valid calculated PKR fare
        ride = Ride.objects.create(
            passenger=request.user,
            pickup_address=pickup_address,
            pickup_lat=pickup_lat,
            pickup_lng=pickup_lng,
            dropoff_address=dropoff_address,
            dropoff_lat=dropoff_lat,
            dropoff_lng=dropoff_lng,
            fare=fare,
            booked_seats=requested_seats,
            scheduled_time=scheduled_time if scheduled_time else None,
            status=status
        )

        # Create booking record
        RideBooking.objects.create(
            ride=ride,
            passenger=request.user,
            seats_booked=requested_seats
        )

        return redirect('track_ride', ride_id=ride.id)

    return render(request, 'book_ride.html')



@login_required
def book_ride_seat(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)
    if request.method == 'POST':
        seats_to_book = int(request.POST.get('seats_to_book', 1))
        
        # Ensure enough seats are available
        available_seats = ride.total_seats - ride.booked_seats
        if seats_to_book <= available_seats:
            ride.booked_seats += seats_to_book
            ride.save()
            
            RideBooking.objects.create(
                ride=ride,
                passenger=request.user,
                seats_booked=seats_to_book
            )
    return redirect('track_ride', ride_id=ride.id)

from .models import Notification
@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'index'))

@login_required
def accept_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)
    if not ride.driver:
        ride.driver = request.user
        ride.status = 'accepted'
        ride.save()
    return redirect('track_ride', ride_id=ride.id)

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Ride, RideBooking, UserProfile, DriverProfile

@login_required(login_url='login')
def track_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)
    
    # Calculate available seats safely
    available_seats = max(0, ride.total_seats - ride.booked_seats)
    
    # User Profile & Driver Verification
    profile = UserProfile.objects.filter(user=request.user).first()
    is_driver = (profile.role == 'driver') if profile else False
    
    driver_approved = False
    if is_driver:
        try:
            driver_profile = DriverProfile.objects.get(user_profile=profile)
            driver_approved = driver_profile.is_approved
        except DriverProfile.DoesNotExist:
            driver_approved = False

    # Fetch all bookings for this ride
    bookings = ride.bookings.select_related('passenger', 'passenger__profile').all()
    user_booking = RideBooking.objects.filter(ride=ride, passenger=request.user).first()
    user_has_booked = user_booking is not None
    
    # --- FARE SPLITTING LOGIC ---
    # Calculate current user's portion of the fare based on booked seats
    user_fare = 0.0
    if ride.booked_seats > 0 and user_has_booked:
        user_fare = round((float(ride.fare) / ride.booked_seats) * user_booking.seats_booked, 2)
    elif user_has_booked:
        user_fare = float(ride.fare)

    # --- POST ACTION HANDLERS ---
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # 1. Join / Book Seats (Allowed in 'requested' OR 'accepted' state)
        if action in ['join_ride', 'book_seat']:
            if ride.status in ['requested', 'accepted']:
                try:
                    seats_requested = int(request.POST.get('seats_to_book', 1))
                except ValueError:
                    seats_requested = 1
                    
                if not user_has_booked and request.user != ride.passenger:
                    if 1 <= seats_requested <= available_seats:
                        RideBooking.objects.create(
                            ride=ride,
                            passenger=request.user,
                            seats_booked=seats_requested
                        )
                        ride.booked_seats += seats_requested
                        ride.save()
            return redirect('track_ride', ride_id=ride.id)

        # 2. Cancel Passenger Booking (Reverts available seats)
        elif action == 'cancel_booking' and user_has_booked:
            if ride.status in ['requested', 'accepted']:
                seats_freed = user_booking.seats_booked
                user_booking.delete()
                
                ride.booked_seats = max(0, ride.booked_seats - seats_freed)
                ride.save()
            return redirect('track_ride', ride_id=ride.id)
            
        # 3. Driver Accepts Ride
        elif action == 'accept' and (is_driver and driver_approved):
            new_fare = request.POST.get('modified_fare')
            ride.driver = request.user
            if new_fare:
                try:
                    parsed_fare = float(new_fare)
                    if parsed_fare != float(ride.fare):
                        ride.original_fare = ride.fare
                        ride.fare = parsed_fare
                        ride.fare_verified_by_passenger = False
                    else:
                        ride.fare_verified_by_passenger = True
                except ValueError:
                    pass
            ride.status = 'accepted'
            ride.save()
            return redirect('track_ride', ride_id=ride.id)

        # 4. Driver Starts Ride (Locks all bookings)
        elif action == 'start_ride' and request.user == ride.driver:
            ride.status = 'ongoing'
            ride.save()
            return redirect('track_ride', ride_id=ride.id)

        # 5. Driver Ends Ride
        elif action == 'end_ride' and request.user == ride.driver:
            ride.status = 'completed'
            ride.save()
            return redirect('track_ride', ride_id=ride.id)

        # 6. Entire Ride Cancelation (Driver or Creator)
        elif action == 'cancel_ride' and (request.user == ride.passenger or request.user == ride.driver):
            ride.status = 'canceled'
            ride.save()
            return redirect('track_ride', ride_id=ride.id)

    context = {
        'ride': ride,
        'available_seats': available_seats,
        'user_has_booked': user_has_booked,
        'user_booking': user_booking,
        'user_fare': user_fare,
        'is_driver': is_driver and driver_approved,
        'bookings': bookings,
    }
    return render(request, 'track_ride.html', context)
@login_required
def send_user_message(request, user_id):
    recipient = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        message_content = request.POST.get('message_content')
        if message_content:
            Notification.objects.create(
                recipient=recipient,
                sender=request.user,
                title=f"Message from {request.user.username}",
                content=message_content
            )
    return redirect(request.META.get('HTTP_REFERER', 'index'))

@login_required
def send_user_message(request, ride_id, user_id):
    ride = get_object_or_404(Ride, id=ride_id)
    recipient = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        message_content = request.POST.get('message_content')
        if message_content:
            Notification.objects.create(
                recipient=recipient,
                sender=request.user,
                ride=ride, # Attach the ride automatically
                title=f"Message regarding Ride #{ride.id}",
                content=message_content
            )
    return redirect(request.META.get('HTTP_REFERER', 'index'))


from django.http import JsonResponse

@login_required
def fetch_notifications_api(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:10]
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    
    notif_data = []
    for notif in notifications:
        notif_data.append({
            'id': notif.id,
            'title': notif.title,
            'content': notif.content,
            'is_read': notif.is_read,
            'created_at': notif.created_at.strftime('%b %d, %H:%M'),
            'ride_id': notif.ride.id if notif.ride else None,
            'sender_id': notif.sender.id if notif.sender else None,
            'sender_username': notif.sender.username if notif.sender else "System",
        })
        
    return JsonResponse({
        'unread_count': unread_count,
        'notifications': notif_data
    })
    
    
from .models import Ride, Rating
@login_required(login_url='login')
def start_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)
    # Ensure current user is the driver
    if ride.status == 'accepted':
        ride.status = 'ongoing'
        ride.save()
        messages.success(request, 'Ride started successfully!')
    return redirect('track_ride', ride_id=ride.id)

@login_required(login_url='login')
def complete_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)
    if ride.status == 'ongoing':
        ride.status = 'completed'
        ride.save()
        messages.success(request, 'Ride completed!')
    return redirect('track_ride', ride_id=ride.id)


@login_required(login_url='login')
def submit_rating(request, ride_id):
    if request.method == 'POST':
        ride = get_object_or_404(Ride, id=ride_id)
        
        # Determine who is receiving the rating
        if request.user == ride.passenger:
            given_to = ride.driver
        else:
            given_to = ride.passenger

        score = request.POST.get('score')
        comment = request.POST.get('comment', '')

        if given_to and score:
            Rating.objects.update_or_create(
                ride=ride,
                given_by=request.user,
                given_to=given_to,
                defaults={
                    'score': int(score),
                    'comment': comment
                }
            )
            messages.success(request, 'Thank you! Your rating has been submitted.')
        else:
            messages.error(request, 'Unable to submit rating.')

    return redirect('track_ride', ride_id=ride_id)


@login_required
def live_location_page(request):
    return render(request, 'live_location.html')