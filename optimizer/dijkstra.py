import heapq
from .factors import weather_factor, cargo_factor
from .graph_utils import graph
from .traffic_api import get_live_traffic_factor

def dijkstra(graph, start, end, weather, traffic=None, cargo=None):
    queue = [(0, start, [])]
    seen = set()

    while queue:
        cost, node, path = heapq.heappop(queue)
        if node in seen:
            continue
        path = path + [node]
        seen.add(node)

        if node == end:
            return {
                "route": path,
                "total_distance": round(cost, 2)
            }

        for neighbor, base_weight in graph.get(node, {}).items():
            # Smart adjustment factors
            w_factor = weather_factor(weather)
            c_factor = cargo_factor(cargo)

            try:
                t_factor = get_live_traffic_factor(node, neighbor)
            except Exception as e:
                print(f"[Traffic API error] {node} → {neighbor}: {e}")
                t_factor = 1.0

            adjusted_weight = base_weight * w_factor * t_factor * c_factor
            heapq.heappush(queue, (cost + adjusted_weight, neighbor, path))

    return {
        "route": [],
        "total_distance": float("inf"),
        "error": "No path found"
    }

