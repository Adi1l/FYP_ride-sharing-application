import math
from datetime import datetime
import requests

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points 
    on the earth (specified in decimal degrees) in kilometers.
    """
    if not lat1 or not lon1 or not lat2 or not lon2:
        return 0.0
        
    lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)  # returns distance in km



def calculate_recommended_fare(lat1, lon1, lat2, lon2):
    # 1. Base distance calculation
    distance_km = calculate_distance(lat1, lon1, lat2, lon2)
    
    base_fare = 150.0  # Base fixed starting charge (e.g., in PKR or your local currency)
    rate_per_km = 40.0 # Cost per kilometer
    
    fare = base_fare + (distance_km * rate_per_km)
    
    # 2. Peak Hours Multiplier (e.g., Morning 8 AM - 10 AM, Evening 5 PM - 8 PM)
    current_hour = datetime.now().hour
    is_peak_hour = (8 <= current_hour <= 10) or (17 <= current_hour <= 20)
    
    if is_peak_hour:
        fare *= 1.3  # 30% surge during peak hours
        
    # 3. Weather Multiplier (Optional check using OpenWeatherMap)
    # You can sign up for a free OpenWeather API key if you want real-time checks
    try:
        # Example using a placeholder API call - replace with your API key if needed
        api_key = "YOUR_OPENWEATHER_API_KEY"
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat1}&lon={lon1}&appid={api_key}"
        response = requests.get(url, timeout=2).json()
        
        weather_condition = response['weather'][0]['main'].lower()
        if 'rain' in weather_condition or 'snow' in weather_condition or 'storm' in weather_condition:
            fare *= 1.25  # 25% surge for bad weather
    except Exception:
        pass  # Fallback if weather API fails or is not configured
        
    return round(fare, 2)