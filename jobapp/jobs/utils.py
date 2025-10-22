import requests
import json
from django.conf import settings

def geocode_address(address, city, state, country, postal_code=None):
    """
    Geocode an address using Google Maps Geocoding API
    Returns (latitude, longitude) or (None, None) if geocoding fails
    """
    if not settings.GOOGLE_MAPS_API_KEY:
        return None, None

    # Construct the full address
    full_address_parts = []
    if address:
        full_address_parts.append(address.strip())
    if city:
        full_address_parts.append(city.strip())
    if state:
        full_address_parts.append(state.strip())
    if postal_code:
        full_address_parts.append(postal_code.strip())
    if country:
        full_address_parts.append(country.strip())

    full_address = ', '.join(full_address_parts)

    if not full_address:
        return None, None

    try:
        # Google Maps Geocoding API
        url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {
            'address': full_address,
            'key': settings.GOOGLE_MAPS_API_KEY
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data['status'] == 'OK' and data['results']:
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            print(f"Geocoding failed for address '{full_address}': {data.get('status', 'Unknown error')}")
            return None, None

    except Exception as e:
        print(f"Geocoding error for address '{full_address}': {str(e)}")
        return None, None

def reverse_geocode(latitude, longitude):
    """
    Reverse geocode coordinates to get address
    Returns formatted address string or None if reverse geocoding fails
    """
    if not settings.GOOGLE_MAPS_API_KEY:
        return None

    try:
        url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {
            'latlng': f"{latitude},{longitude}",
            'key': settings.GOOGLE_MAPS_API_KEY
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data['status'] == 'OK' and data['results']:
            return data['results'][0]['formatted_address']
        else:
            return None

    except Exception as e:
        print(f"Reverse geocoding error for coordinates ({latitude}, {longitude}): {str(e)}")
        return None
