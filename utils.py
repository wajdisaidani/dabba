import random
import string
from datetime import datetime

def generate_mock_coordinates():
    """Generate mock GPS coordinates within Europe"""
    # European coordinate ranges
    lat = round(random.uniform(35.0, 71.0), 6)  # Latitude range for Europe
    lng = round(random.uniform(-10.0, 40.0), 6)  # Longitude range for Europe
    return lat, lng

def generate_transaction_id():
    """Generate a mock transaction ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"TXN{timestamp}{random_suffix}"

def format_currency(amount):
    """Format amount as currency"""
    return f"€{amount:.2f}"

def calculate_distance_price(origin, destination, base_rate=0.5):
    """Mock function to calculate price based on distance"""
    # In a real app, this would use a mapping API
    # For now, return a random price between 10-100
    return round(random.uniform(10.0, 100.0), 2)

def get_shipment_status_color(status):
    """Return CSS class for shipment status"""
    status_colors = {
        'pending': 'warning',
        'booked': 'info',
        'in_transit': 'primary',
        'delivered': 'success',
        'cancelled': 'danger'
    }
    return status_colors.get(status.value if hasattr(status, 'value') else status, 'secondary')

def get_user_type_display(user_type):
    """Return display name for user type"""
    if hasattr(user_type, 'value'):
        return user_type.value.title()
    return str(user_type).title()
