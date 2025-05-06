from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
import random
import datetime
from geopy.distance import geodesic
from flask_cors import CORS

from optimizer.optimizer_core import optimize_route as ai_optimize_route  # ✅ AI-based optimization
from optimizer.graph_utils import graph
from optimizer.factors import weather_factor, traffic_factor, cargo_factor  # Factor adjustments
from traffic_api import get_live_traffic_factor  # Optional: real-time traffic integration

# Keep get_current_weather function inside app.py or import it if external



# --- Flask Setup ---
app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)  # Let Squarespace JS talk to your backend

# Development mode flag
DEV_MODE = True

# --- In-memory data ---
ports = {
    'New York': (40.7128, -74.0060),
    'Los Angeles': (34.0522, -118.2437),
    'Chicago': (41.8781, -87.6298),
    'Houston': (29.7604, -95.3698),
    'Phoenix': (33.4484, -112.0740),
    'Atlanta': (33.7490, -84.3880),
    'Miami': (25.7617, -80.1918),
    'Dallas': (32.7767, -96.7970),
    'Seattle': (47.6062, -122.3321),
    'San Francisco': (37.7749, -122.4194),
    'Denver': (39.7392, -104.9903),
    'Boston': (42.3601, -71.0589),
    'Washington D.C.': (38.9072, -77.0369),
    'Philadelphia': (39.9526, -75.1652),
    'Charlotte': (35.2271, -80.8431),
    'Nashville': (36.1627, -86.7816),
    'Jacksonville': (30.3322, -81.6557),
    'Las Vegas': (36.1699, -115.1398),
    'San Diego': (32.7157, -117.1611),

    # International
    'Hamburg': (53.5501, 9.9937),
    'Conakry': (9.5085, -13.7125),
    'Shanghai': (31.2304, 121.4737),
    'Dubai': (25.276987, 55.296249),
    'Singapore': (1.3521, 103.8198),
    'Rotterdam': (51.9225, 4.47917),
    'Lagos': (6.5244, 3.3792)
}


shipments = []
shipment_id_counter = 1
latest_route = []  # 🔁 This will store the latest optimized route for map display


# --- Helper functions ---

def get_current_weather(lat, lng):
    fake_conditions = [
        "Clear skies", "Partly cloudy", "Overcast", "Light rain",
        "Heavy rain", "Stormy", "Foggy", "Windy", "Snowy"
    ]
    condition = random.choice(fake_conditions)
    temperature = round(random.uniform(15, 35), 1)
    return {"location": f"Lat {lat:.2f}, Lon {lng:.2f}", "temperature": f"{temperature}°C", "condition": condition}

def calculate_distance(origin_coords, destination_coords):
    return geodesic(origin_coords, destination_coords).kilometers

def calculate_cost(distance, weight, shipping_class):
    multiplier = 1
    if shipping_class == 'express':
        multiplier = 1.5
    elif shipping_class == 'heavy_cargo':
        multiplier = 2
    return distance * 2 * weight * multiplier

def calculate_eta(distance, shipping_class):
    speeds = {'standard': 30, 'express': 45, 'heavy_cargo': 20}
    return distance / speeds[shipping_class]

def calculate_current_position(origin_coords, destination_coords, departure_time, shipping_class):
    now = datetime.datetime.now()
    hours_elapsed = (now - departure_time).total_seconds() / 3600
    distance = calculate_distance(origin_coords, destination_coords)
    total_hours = calculate_eta(distance, shipping_class)

    if hours_elapsed >= total_hours:
        return destination_coords, 'Arrived'

    progress = min(hours_elapsed / total_hours, 1.0)
    lat = origin_coords[0] + (destination_coords[0] - origin_coords[0]) * progress
    lng = origin_coords[1] + (destination_coords[1] - origin_coords[1]) * progress
    return (lat, lng), 'In Transit'

# --- Routes ---

@app.route('/')
def index():
    if not DEV_MODE and not session.get('logged_in'):
        return redirect(url_for('login'))

    for shipment in shipments:
        if shipment['status'] in ['In Transit', 'Departed']:
            origin_coords = ports[shipment['origin']]
            destination_coords = ports[shipment['destination']]
            current_position, status = calculate_current_position(
                origin_coords, destination_coords, shipment['departure_time'], shipment['shipping_class']
            )
            shipment['current_position'] = current_position
            shipment['status'] = status

    return render_template('index.html', ports=sorted(ports.keys()), shipments=shipments)

@app.route('/generate_fake_shipments')
def generate_fake_shipments():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    global shipment_id_counter
    for _ in range(20):
        origin = random.choice(list(ports.keys()))
        destination = random.choice(list(ports.keys()))
        while destination == origin:
            destination = random.choice(list(ports.keys()))
        weight = round(random.uniform(5, 500), 2)
        shipping_class = random.choice(['standard', 'express', 'heavy_cargo'])
        origin_coords = ports[origin]
        destination_coords = ports[destination]
        distance = calculate_distance(origin_coords, destination_coords)
        cost = calculate_cost(distance, weight, shipping_class)
        departure_time = datetime.datetime.now()
        eta = departure_time + datetime.timedelta(hours=calculate_eta(distance, shipping_class))

        shipment = {
            'id': shipment_id_counter,
            'origin': origin,
            'destination': destination,
            'weight': weight,
            'shipping_class': shipping_class,
            'distance': distance,
            'cost': cost,
            'status': 'Preparing',
            'departure_time': departure_time,
            'eta': eta,
            'current_position': origin_coords,
            'ship_name': f"Ship-{random.randint(1000,9999)}"
        }
        shipments.append(shipment)
        shipment_id_counter += 1

    flash('Fake shipments generated successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/add_shipment', methods=['POST'])
def add_shipment():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    global shipment_id_counter
    try:
        origin = request.form['origin']
        destination = request.form['destination']
        weight = float(request.form['weight'])
        shipping_class = request.form['shipping_class']

        if origin == destination:
            flash('Origin and destination cannot be the same.', 'error')
            return redirect(url_for('index'))

        origin_coords = ports[origin]
        destination_coords = ports[destination]
        distance = calculate_distance(origin_coords, destination_coords)
        cost = calculate_cost(distance, weight, shipping_class)
        departure_time = datetime.datetime.now()
        eta = departure_time + datetime.timedelta(hours=calculate_eta(distance, shipping_class))

        shipment = {
            'id': shipment_id_counter,
            'origin': origin,
            'destination': destination,
            'weight': weight,
            'shipping_class': shipping_class,
            'distance': distance,
            'cost': cost,
            'status': 'Preparing',
            'departure_time': departure_time,
            'eta': eta,
            'current_position': origin_coords,
            'ship_name': f"Ship-{random.randint(1000,9999)}"
        }
        shipments.append(shipment)
        shipment_id_counter += 1

        flash('Shipment successfully added.', 'success')
    except Exception as e:
        flash(f'Error adding shipment: {e}', 'error')

    return redirect(url_for('index'))

@app.route('/start_shipment/<int:shipment_id>', methods=['POST'])
def start_shipment(shipment_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    for shipment in shipments:
        if shipment['id'] == shipment_id and shipment['status'] == 'Preparing':
            shipment['status'] = 'Departed'
            shipment['departure_time'] = datetime.datetime.now()
            shipment['eta'] = shipment['departure_time'] + datetime.timedelta(
                hours=calculate_eta(shipment['distance'], shipment['shipping_class'])
            )
            flash('Shipment departed.', 'success')
            break

    return redirect(url_for('index'))

from optimizer.optimizer_core import optimize_route as ai_optimize_route

@app.route('/ai_optimize_route', methods=['POST'])
def ai_optimize_route_handler():
    global latest_route  # 💾 make latest_route accessible here

    data = request.get_json()
    from_city = data.get('from')
    to_city = data.get('to')
    traffic = data.get('traffic', 'medium')
    cargo = data.get('cargo_type', 'general')

    if from_city not in graph or to_city not in graph:
        return jsonify({"error": "Invalid city name."}), 400

    origin_coords = ports.get(from_city)
    destination_coords = ports.get(to_city)

    if not origin_coords or not destination_coords:
        return jsonify({"error": "Missing coordinates for city"}), 400

    origin_weather = get_current_weather(*origin_coords)
    destination_weather = get_current_weather(*destination_coords)

    condition_priority = {
        "Clear skies": 1, "Partly cloudy": 2, "Overcast": 3,
        "Light rain": 4, "Foggy": 4, "Windy": 5,
        "Heavy rain": 6, "Stormy": 7, "Snowy": 8
    }

    weather = max(
        [origin_weather["condition"], destination_weather["condition"]],
        key=lambda x: condition_priority.get(x, 0)
    )

    result = ai_optimize_route(from_city, to_city, weather, traffic, cargo)

    result['weather_used'] = weather
    result['origin_weather'] = origin_weather
    result['destination_weather'] = destination_weather

    # 💾 Save route for map display
    latest_route = result.get('route', [])

    return jsonify(result)



@app.route('/document_suggestion', methods=['GET', 'POST'])
def document_suggestion():
    suggested_docs = []

    if request.method == 'POST':
        origin = request.form['origin']
        destination = request.form['destination']
        weight = float(request.form['weight'])
        cost = float(request.form['cost'])

        suggested_docs.append("Bill of Lading (BOL)")
        if origin != destination:
            suggested_docs.append("Customs Declaration Form")
        if weight >= 10000:
            suggested_docs.append("Heavy Cargo Special Permit")
        if cost >= 10000:
            suggested_docs.append("Insurance Certificate")

    # 👇 this must be inside the function
    static_docs = [
        {"name": "Bill of Lading", "filename": "bill_of_lading.pdf"},
        {"name": "Customs Declaration", "filename": "customs_declaration.pdf"},
        {"name": "Heavy Cargo Permit", "filename": "heavy_cargo_permit.pdf"},
        {"name": "Insurance Certificate", "filename": "insurance_certificate.pdf"},
    ]

    return render_template(
        'document_suggestion.html',
        ports=sorted(ports.keys()),
        suggested_docs=suggested_docs,
        static_docs=static_docs
    )

@app.route("/analytics")
def analytics():
    stats = {
        "total_shipments": 150,
        "active_shipments": 42,
        "completed_shipments": 108,
        "total_distance": 125000,
        "total_cost": 328500.75,
        "avg_cost_per_km": 2.63,
    }

    shipping_classes = {
        "standard": 80,
        "express": 45,
        "heavy_cargo": 25,
    }

    top_origins = [("New York", 35), ("Shanghai", 30), ("Rotterdam", 25), ("Dubai", 20), ("Singapore", 18)]
    top_destinations = [("Los Angeles", 33), ("Hamburg", 28), ("Tokyo", 26), ("Cape Town", 22), ("Mumbai", 20)]
    top_routes = [("NY → LA", 85000.00), ("Shanghai → Tokyo", 72000.00), ("Dubai → Hamburg", 61000.00), ("Rotterdam → Cape Town", 56000.00), ("Singapore → Mumbai", 55000.00)]

    weather = {
        "location": "New York",
        "temperature": "22°C",
        "condition": "Partly Cloudy",
    }

    return render_template("analytics.html",
                           stats=stats,
                           shipping_classes=shipping_classes,
                           top_origins=top_origins,
                           top_destinations=top_destinations,
                           top_routes=top_routes,
                           weather=weather)

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route('/route-form')
def route_form():
    return render_template('route_form.html')

@app.route("/map")
def route_map():
    print("🔥 Latest route sent to map:", latest_route)
    return render_template("route_map.html", route=latest_route or ["Chicago", "Houston"])

@app.route("/map-test")
def test_map():
    return render_template("route_map_test.html")

# Add this to app.py
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    result = {}
    route = []
    
    if request.method == "POST":
        from_city = request.form.get("from")
        to_city = request.form.get("to")
        cargo = request.form.get("cargo")
        traffic = request.form.get("traffic", "medium")

        origin_coords = ports.get(from_city)
        dest_coords = ports.get(to_city)

        origin_weather = get_current_weather(*origin_coords)
        destination_weather = get_current_weather(*dest_coords)

        condition_priority = {
            "Clear skies": 1, "Partly cloudy": 2, "Overcast": 3,
            "Light rain": 4, "Foggy": 4, "Windy": 5,
            "Heavy rain": 6, "Stormy": 7, "Snowy": 8
        }

        weather = max(
            [origin_weather["condition"], destination_weather["condition"]],
            key=lambda x: condition_priority.get(x, 0)
        )

        result = ai_optimize_route(from_city, to_city, weather, traffic, cargo)
        result["origin_weather"] = origin_weather
        result["destination_weather"] = destination_weather
        result["weather_used"] = weather

        route = result.get("route", [])

    return render_template("dashboard.html", ports=sorted(ports.keys()), result=result, route=route)

@app.route('/api/weather')
def get_weather():
    return jsonify({
        "temp": 72,
        "condition": "Mostly Sunny in Philly"
    })

@app.route('/api/todo')
def get_todo():
    return jsonify([
        {"task": "Refuel Truck 7"},
        {"task": "Check oil on Truck 2"}
    ])

@app.route('/api/stats')
def get_stats():
    return jsonify({
        "fleet_size": 8,
        "on_time_deliveries": "91%",
        "active_routes": 3
    })





if __name__ == "__main__":
    app.run(debug=True)




