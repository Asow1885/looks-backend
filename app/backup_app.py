from flask import Flask, render_template, request
import folium
from geopy.distance import geodesic

app = Flask(__name__)

# Ports with coordinates (latitude, longitude)
ports = {
    "Conakry, Guinea": (9.5095, -13.7122),
    "Hamburg, Germany": (53.5511, 9.9937),
    "Bremen, Germany": (53.0793, 8.8017),
    "Duisburg, Germany": (51.4344, 6.7628),
    "Frankfurt, Germany": (50.1109, 8.6821),
}

# Shipping cost per kilometer (flat rate for simplicity)
RATE_PER_KM = 2  # $2 per kilometer

# Create map with port markers
m = folium.Map(location=[51.1657, 10.4515], zoom_start=5)

# Add port markers to the map
for port, coords in ports.items():
    folium.Marker(
        location=coords,
        popup=f'{port}',
        icon=folium.Icon(color='blue', icon='cloud', prefix='fa')
    ).add_to(m)

# Function to calculate the distance between two ports
def calculate_distance(port1_coords, port2_coords):
    return geodesic(port1_coords, port2_coords).kilometers

# Function to calculate the shipping cost based on distance and weight
def calculate_cost(distance, weight):
    # Simple formula: cost = distance * rate per km * weight (adjust as needed)
    return distance * RATE_PER_KM * weight

@app.route('/')
def index():
    return render_template('index.html', map=m._repr_html_(), ports=ports)

@app.route('/calculate', methods=['POST'])
def calculate():
    # Get port selections and weight from the form
    port1 = request.form['port1']
    port2 = request.form['port2']
    weight = float(request.form['weight'])  # Weight in kg
    
    # Get coordinates for the selected ports
    port1_coords = ports[port1]
    port2_coords = ports[port2]

    # Calculate distance and cost
    distance = calculate_distance(port1_coords, port2_coords)
    cost = calculate_cost(distance, weight)

    return render_template('index.html', map=m._repr_html_(), distance=distance, cost=cost, ports=ports)

if __name__ == '__main__':
    app.run(debug=True)

