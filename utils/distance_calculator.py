import math

# Haversine formula to calculate the distance between two ports
def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distance in kilometers
    distance = R * c
    return distance

# Test the function with two ports (lat, lon)
port_1 = (52.3779, 4.9009)  # Example: Port of Rotterdam
port_2 = (40.7128, -74.0060)  # Example: Port of New York

# Call the function and print the distance
distance = haversine(port_1[0], port_1[1], port_2[0], port_2[1])
print(f"Distance between the ports: {distance:.2f} km")
