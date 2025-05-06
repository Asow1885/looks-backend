from flask import Flask, render_template, request, redirect, url_for, flash
import random
import datetime
import requests
import sqlite3
from geopy.distance import geodesic

app = Flask(__name__, template_folder='templates')
app.secret_key = 'shipping_app_secret_key'
DB_PATH = 'shipping.db'

# Ports (sample)
ports = {
    'New York': (40.7128, -74.0060),
    'Los Angeles': (34.0522, -118.2437),
    'Hamburg': (53.5501, 9.9937),
    'Conakry': (9.5085, -13.7125),
    'Shanghai': (31.2304, 121.4737),
    'Dubai': (25.276987, 55.296249),
    'Singapore': (1.3521, 103.8198),
    'Rotterdam': (51.9225, 4.47917),
    'Lagos': (6.5244, 3.3792)
}

# Weather API Setup
WEATHER_API_KEY = "YOUR_API_KEY_HERE"  # <<< Replace with your real WeatherAPI key

# Cost Settings
RATE_PER_KM = 2  # $2 per kilometer

# Ship speeds
SHIP_SPEED = {
    'standard': 30,      
    'express': 45,       
    'heavy_cargo': 20
}

# Initialize Database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
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

init_db()

# Calculate distance
def calculate_distance(origin, destination):
    return geodesic(origin, destination).kilometers

# Calculate cost
def calculate_cost(distance, weight, shipping_class):
    base_rate = RATE_PER_KM
    multiplier = 1
    if shipping_class == 'express':
        multiplier = 1.5
    elif shipping_class == 'heavy_cargo':
        multiplier = 2
    return distance * base_rate * weight * multiplier

# Get Weather
def get_current_weather(lat, lon):
    try:
        url = "https://api.weatherapi.com/v1/current.json"
        params = {
            "key": WEATHER_API_KEY,
            "q": f"{lat},{lon}",
            "aqi": "no"
        }
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        weather_info = {
            "location": data["location"]["name"],
            "temp_c": data["current"]["temp_c"],
            "wind_kph": data["current"]["wind_kph"],
            "condition": data["current"]["condition"]["text"],
            "icon_url": "https:" + data["current"]["condition"]["icon"]
        }
        return weather_info
    except Exception as e:
        print(f"Weather API error: {e}")
        return None

# Save shipment to DB
def add_shipment_to_db(shipment_data):
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
        shipment_data['departure_time'],
        shipment_data['eta']
    ))
    conn.commit()
    conn.close()

# Get shipments
def get_shipments():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM shipments ORDER BY id DESC')
    shipments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return shipments

# Generate fake shipments
def generate_fake_shipments(num_shipments=20):
    for _ in range(num_shipments):
        origin = random.choice(list(ports.keys()))
        destination = random.choice(list(ports.keys()))
        while destination == origin:
            destination = random.choice(list(ports.keys()))
        
        weight = round(random.uniform(5.0, 500.0), 2)
        shipping_class = random.choice(['standard', 'express', 'heavy_cargo'])
        
        origin_coords = ports[origin]
        destination_coords = ports[destination]
        
        distance = calculate_distance(origin_coords, destination_coords)
        cost = calculate_cost(distance, weight, shipping_class)
        
        shipment_data = {
            'ship_name': f"Ship-{random.randint(1000,9999)}",
            'origin': origin,
            'destination': destination,
            'weight': weight,
            'shipping_class': shipping_class,
            'distance': distance,
            'cost': cost,
            'status': 'Preparing',
            'departure_time': None,
            'eta': None
        }
        
        add_shipment_to_db(shipment_data)

# ========== ROUTES ==========

# Home Page
@app.route('/')
def index():
    shipments = get_shipments()
    return render_template('index.html', ports=sorted(ports.keys()), shipments=shipments)

# Analytics Dashboard
@app.route('/analytics')
def analytics():
    shipments = get_shipments()

    default_port_coords = ports["New York"]
    weather = get_current_weather(default_port_coords[0], default_port_coords[1])

    stats = {
        'total_shipments': len(shipments),
        'active_shipments': sum(1 for s in shipments if s['status'] in ['Preparing', 'Departed', 'In Transit']),
        'completed_shipments': sum(1 for s in shipments if s['status'] == 'Arrived'),
        'total_distance': sum(s['distance'] for s in shipments),
        'total_cost': sum(s['cost'] for s in shipments),
        'avg_cost_per_km': sum(s['cost'] for s in shipments) / sum(s['distance'] for s in shipments) if shipments else 0
    }

    shipping_classes = {
        'standard': sum(1 for s in shipments if s['shipping_class'] == 'standard'),
        'express': sum(1 for s in shipments if s['shipping_class'] == 'express'),
        'heavy_cargo': sum(1 for s in shipments if s['shipping_class'] == 'heavy_cargo')
    }

    origin_counts = {}
    for s in shipments:
        origin_counts[s['origin']] = origin_counts.get(s['origin'], 0) + 1
    top_origins = sorted(origin_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    dest_counts = {}
    for s in shipments:
        dest_counts[s['destination']] = dest_counts.get(s['destination'], 0) + 1
    top_destinations = sorted(dest_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    route_profits = {}
    for s in shipments:
        route = f"{s['origin']} to {s['destination']}"
        route_profits[route] = route_profits.get(route, 0) + s['cost']
    top_routes = sorted(route_profits.items(), key=lambda x: x[1], reverse=True)[:5]

    return render_template('analytics.html',
        stats=stats,
        shipping_classes=shipping_classes,
        top_origins=top_origins,
        top_destinations=top_destinations,
        top_routes=top_routes,
        weather=weather
    )


# Route to generate fake shipments
@app.route('/generate_fake_shipments')
def generate_fake_shipments_route():
    generate_fake_shipments(20)
    flash('✅ 20 fake shipments generated successfully!', 'success')
    return redirect(url_for('index'))

# ========== END ROUTES ==========

if __name__ == '__main__':
    app.run(debug=True, port=5000)


