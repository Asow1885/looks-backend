from .graph_utils import graph
from .dijkstra import dijkstra

def optimize_route(origin, destination, weather, traffic, cargo):
    """
    Real implementation using Dijkstra algorithm and weighted graph.

    Params:
        origin (str): Starting city
        destination (str): Ending city
        weather (str): Weather condition (e.g., 'Clear skies', 'Stormy')
        traffic (str): Traffic level (e.g., 'low', 'medium', 'high')
        cargo (str): Cargo type (e.g., 'general', 'fragile', 'hazmat')

    Returns:
        dict: Contains route path, total adjusted distance, and factors used
    """

    if origin not in graph or destination not in graph:
        return {
            "route": [],
            "total_distance": float("inf"),
            "error": "Invalid city name"
        }

    result = dijkstra(graph, origin, destination, weather, traffic, cargo)
    return result

