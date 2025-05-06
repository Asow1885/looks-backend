from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from geopy.distance import geodesic
import datetime
import random
import sqlite3

app = Flask(__name__, template_folder='templates')
app.config['DEBUG'] = True
app.secret_key = 'shipping_app_secret_key'

# Database setup
DB_PATH = 'shipping.db'

# Predefined ports with their coordinates (latitude, longitude)
ports = {
    'New York': (40.7128, -74.0060),
    'Los Angeles': (34.0522, -118.2437),
    'Hamburg': (53.5501, 9.9937),
    'Conakry': (9.5085, -13.7125),
    'Shanghai': (31.2304, 121.4737),
    'Dubai': (25.276987, 55.296249),
    'Singapore': (1.3521, 103.8198),
    'Rotterdam': (51.9225, 4.47917),
    'Busan': (35.1796, 129.0756),
    'Antwerp': (51.2194, 4.4025),
    'Tokyo': (35.6762, 139.6503),
    'Hong Kong': (22.3193, 114.1694),
    'London': (51.5074, -0.1278),
    'Paris': (48.8566, 2.3522),
    'Sydney': (-33.8688, 151.2093),
    'Miami': (25.7617, -80.1918),
    'Cape Town': (-33.9249, 18.4241),
    'Lagos': (6.5244, 3.3792),
    'Rio de Janeiro': (-22.9068, -43.1729),
    'Mumbai': (19.0760, 72.8777),
    'Manila': (14.5995, 120.9842),
    'Jeddah': (21.2854, 39.2376),
    'Karachi': (24.8607, 67.0011),
    'Suez': (30.5852, 32.2659),
    'Shenzhen': (22.5431, 114.0579),
    'Kaohsiung': (22.6163, 120.3121),
    'Istanbul': (41.0082, 28.9784),
    'Genoa': (44.4056, 8.9463),
    'Valencia': (39.4699, -0.3763),
    'Barcelona': (41.3784, 2.1924),
    'Kolkata': (22.5726, 88.3639),
    'Kuala Lumpur': (3.139, 101.6869),
    'Buenos Aires': (-34.6037, -58.3816),
    'Piraeus': (37.9478, 23.6409),
    'Cairo': (30.0444, 31.2357),
    'Port Said': (31.2653, 32.3036),
    'Bremen': (53.0793, 8.8017),
    'Helsinki': (60.1692, 24.9402),
    'Gothenburg': (57.7089, 11.9746),
    'Dakar': (14.6928, -17.4467),
    'Mombasa': (-4.0435, 39.6682),
    'Douala': (4.0511, 9.7043),
    'Tanger-Med': (35.9131, -5.3579),
    'Zarate': (-34.0819, -59.0152),
    'Port of Karachi': (24.8607, 67.0011),
    'Tianjin': (39.0842, 117.2009),
    'Ningbo': (29.8683, 121.5440),
    'Xiamen': (24.4794, 118.0819),
}

# Shipping constants
RATE_PER_KM = 2  # $2 per kilometer
SHIP_SPEED = {
    'standard': 30,      # 30 km/h
    'express': 45,       # 45 km/h
    'heavy_cargo': 20    # 20 km/h
}

def init_db():
    """Initialize the database with necessary tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create shipments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ship_name TEXT,
        origin TEXT,
        destination TEXT,
        weight REAL,
        shipping_class TEXT,
        distance REAL,
        cost REAL,
        status TEXT,
        departure_time TIMESTAMP,
        eta TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

# Initialize database at startup
init_db()

def calculate_distance(port1_coords, port2_coords):
    """Calculate distance between two ports using geodesic."""
    return geodesic(port1_coords, port2_coords).kilometers

def calculate_cost(distance, weight, shipping_class):
    """Calculate shipping cost."""
    base_rate = RATE_PER_KM
    if shipping_class == 'express':
        rate_multiplier = 1.5
    elif shipping_class == 'heavy_cargo':
        rate_multiplier = 2
    else:
        rate_multiplier = 1
    return distance * base_rate * weight * rate_multiplier

def calculate_eta(distance, shipping_class):
    """Calculate estimated time of arrival in hours."""
    speed = SHIP_SPEED[shipping_class]
    return distance / speed

def calculate_current_position(origin_coords, destination_coords, departure_time, shipping_class):
    """Calculate current ship position based on departure time and speed."""
    if departure_time is None:
        return origin_coords, "Preparing"
        
    now = datetime.datetime.now()
    hours_elapsed = (now - departure_time).total_seconds() / 3600
    
    # Calculate total journey duration
    distance = calculate_distance(origin_coords, destination_coords)
    total_hours = distance / SHIP_SPEED[shipping_class]
    
    # If ship has arrived, return destination
    if hours_elapsed >= total_hours:
        return destination_coords, 'Arrived'
    
    # Calculate progress as a percentage
    progress = min(hours_elapsed / total_hours, 1.0)
    
    # Interpolate between origin and destination
    current_lat = origin_coords[0] + (destination_coords[0] - origin_coords[0]) * progress
    current_lng = origin_coords[1] + (destination_coords[1] - origin_coords[1]) * progress
    
    return (current_lat, current_lng), 'In Transit'

# Database functions
def get_shipments():
    """Get all shipments from the database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM shipments ORDER BY id DESC')
    shipments_rows = cursor.fetchall()
    
    # Convert to list of dictionaries
    shipments = []
    for row in shipments_rows:
        shipment = dict(row)
        
        # Parse timestamps from string to datetime
        if shipment['departure_time']:
            shipment['departure_time'] = datetime.datetime.fromisoformat(shipment['departure_time'])
        if shipment['eta']:
            shipment['eta'] = datetime.datetime.fromisoformat(shipment['eta'])
            
        # Set current position based on status
        if shipment['status'] == 'Preparing':
            shipment['current_position'] = ports[shipment['origin']]
        elif shipment['status'] == 'Arrived':
            shipment['current_position'] = ports[shipment['destination']]
        else:
            # Calculate current position for in-transit shipments
            origin_coords = ports[shipment['origin']]
            destination_coords = ports[shipment['destination']]
            current_position, status = calculate_current_position(
                origin_coords, 
                destination_coords, 
                shipment['departure_time'], 
                shipment['shipping_class']
            )
            shipment['current_position'] = current_position
            
            # Update status in the database if needed
            if status != shipment['status']:
                update_shipment_status(shipment['id'], status)
                shipment['status'] = status
                
        shipments.append(shipment)
    
    conn.close()
    return shipments

def add_shipment_to_db(shipment_data):
    """Add a new shipment to the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO shipments (
        ship_name, origin, destination, weight, shipping_class, 
        distance, cost, status, departure_time, eta
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        shipment_data['ship_name'],
        shipment_data['origin'],
        shipment_data['destination'],
        shipment_data['weight'],
        shipment_data['shipping_class'],
        shipment_data['distance'],
        shipment_data['cost'],
        shipment_data['status'],
        shipment_data['departure_time'].isoformat() if shipment_data['departure_time'] else None,
        shipment_data['eta'].isoformat() if shipment_data['eta'] else None
    ))
    
    shipment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return shipment_id

def update_shipment_status(shipment_id, status):
    """Update a shipment's status in the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        'UPDATE shipments SET status = ? WHERE id = ?', 
        (status, shipment_id)
    )
    
    conn.commit()
    conn.close()

def start_shipment_in_db(shipment_id):
    """Update shipment to 'Departed' status with current departure time"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get shipment info
    cursor.execute('SELECT origin, destination, shipping_class FROM shipments WHERE id = ?', (shipment_id,))
    shipment = cursor.fetchone()
    
    if not shipment:
        conn.close()
        return False
    
    # Calculate updated ETA
    origin_coords = ports[shipment[0]]
    destination_coords = ports[shipment[1]]
    distance = calculate_distance(origin_coords, destination_coords)
    eta_hours = calculate_eta(distance, shipment[2])
    
    departure_time = datetime.datetime.now()
    eta = departure_time + datetime.timedelta(hours=eta_hours)
    
    # Update shipment
    cursor.execute(
        'UPDATE shipments SET status = ?, departure_time = ?, eta = ? WHERE id = ?', 
        ('Departed', departure_time.isoformat(), eta.isoformat(), shipment_id)
    )
    
    conn.commit()
    conn.close()
    return True

@app.route('/')
def index():
    shipments = get_shipments()
    return render_template('index.html', ports=sorted(ports.keys()), shipments=shipments)

@app.route('/get_ports_data')
def get_ports_data():
    """API endpoint to get port coordinates for the map"""
    ports_data = {name: {"lat": coords[0], "lng": coords[1]} for name, coords in ports.items()}
    print("Ports data endpoint called - returning data for", len(ports_data), "ports")
    return jsonify(ports_data)

@app.route('/get_shipments_data')
def get_shipments_data():
    """API endpoint to get shipment data for the map"""
    shipments = get_shipments()
    
    shipments_data = []
    for shipment in shipments:
        origin_name = shipment['origin']
        destination_name = shipment['destination']
        origin_coords = ports[origin_name]
        destination_coords = ports[destination_name]
        
        # Format ETA for display
        eta_display = shipment['eta'].strftime('%Y-%m-%d %H:%M') if shipment['eta'] else 'Unknown'
        
        shipments_data.append({
            'id': shipment['id'],
            'origin': {
                'name': origin_name,
                'lat': origin_coords[0],
                'lng': origin_coords[1]
            },
            'destination': {
                'name': destination_name,
                'lat': destination_coords[0],
                'lng': destination_coords[1]
            },
            'current_position': {
                'lat': shipment['current_position'][0],
                'lng': shipment['current_position'][1]
            },
            'shipping_class': shipment['shipping_class'],
            'status': shipment['status'],
            'ship_name': shipment['ship_name'],
            'eta': eta_display
        })
    
    print("Shipments data endpoint called - returning data for", len(shipments_data), "shipments")
    return jsonify(shipments_data)

if __name__ == '__main__':
    print("Starting database version of shipping app...")
    print("Access the app at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)

# Add this new route to your app_db.py
@app.route('/analytics')
def analytics():
    """Display analytics dashboard with charts and insights"""
    # Get all shipments
    shipments = get_shipments()
    
    # Calculate statistics
    stats = {
        'total_shipments': len(shipments),
        'active_shipments': sum(1 for s in shipments if s['status'] in ['Preparing', 'Departed', 'In Transit']),
        'completed_shipments': sum(1 for s in shipments if s['status'] == 'Arrived'),
        'total_distance': sum(s['distance'] for s in shipments),
        'total_cost': sum(s['cost'] for s in shipments),
        'avg_cost_per_km': sum(s['cost'] for s in shipments) / sum(s['distance'] for s in shipments) if shipments else 0
    }
    
    # Calculate shipping class distribution
    shipping_classes = {
        'standard': sum(1 for s in shipments if s['shipping_class'] == 'standard'),
        'express': sum(1 for s in shipments if s['shipping_class'] == 'express'),
        'heavy_cargo': sum(1 for s in shipments if s['shipping_class'] == 'heavy_cargo')
    }
    
    # Calculate top origin ports
    origin_counts = {}
    for s in shipments:
        origin_counts[s['origin']] = origin_counts.get(s['origin'], 0) + 1
    top_origins = sorted(origin_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Calculate top destination ports
    dest_counts = {}
    for s in shipments:
        dest_counts[s['destination']] = dest_counts.get(s['destination'], 0) + 1
    top_destinations = sorted(dest_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Calculate most profitable routes
    route_profits = {}
    for s in shipments:
        route = f"{s['origin']} to {s['destination']}"
        route_profits[route] = route_profits.get(route, 0) + s['cost']
    top_routes = sorted(route_profits.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return render_template(
        'analytics.html', 
        stats=stats,
        shipping_classes=shipping_classes,
        top_origins=top_origins,
        top_destinations=top_destinations,
        top_routes=top_routes
    )