def optimize_route(origin, destination, weather, traffic, cargo):
    """
    Real implementation using Dijkstra algorithm and weighted graph.

    Params:
        origin (str)
        destination (str)
        weather (str)
        traffic (str)
        cargo (str)

    Returns:
        dict: route path, total distance, and any conditions used
    """
    if origin not in graph or destination not in graph:
        return {
            "route": [],
            "total_distance": float("inf"),
            "error": "Invalid city name"
        }

    result = dijkstra(graph, origin, destination, weather, traffic, cargo)
    return result
