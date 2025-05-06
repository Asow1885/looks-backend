from geopy.distance import geodesic

def calculate_distance(port1_coords, port2_coords):
    """
    Calculate the distance between two ports using their latitude and longitude coordinates.

    Args:
        port1_coords (tuple): (latitude, longitude) of port 1
        port2_coords (tuple): (latitude, longitude) of port 2

    Returns:
        float: distance in kilometers between port 1 and port 2
    """
    distance = geodesic(port1_coords, port2_coords).kilometers
    return distance

# Example usage:
port_1 = (40.7128, -74.0060)  # New York (latitude, longitude)
port_2 = (34.0522, -118.2437)  # Los Angeles (latitude, longitude)

distance = calculate_distance(port_1, port_2)

print(f"The distance between the ports is {distance:.2f} km")
