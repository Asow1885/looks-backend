# quick_start.py
"""
Quick start example showing basic route optimization functionality
"""

import numpy as np
import matplotlib.pyplot as plt
from src.models.route_optimizer import LogisticsRouteOptimizer
from src.models.finance_analyzer import LogisticsFinanceAnalyzer

def run_example():
    """Run a simple logistics route optimization example."""
    print("=" * 60)
    print("Logistics AI - Route Optimization Example")
    print("=" * 60)
    
    # Sample location data (x, y coordinates)
    locations = [
        (0, 0),     # Depot
        (10, 10),   # Location 1
        (20, 20),   # Location 2
        (-10, 10),  # Location 3
        (-20, -20), # Location 4
        (30, -10),  # Location 5
        (-30, 10),  # Location 6
        (25, 25),   # Location 7
        (15, -15),  # Location 8
        (-15, -5),  # Location 9
    ]
    
    # Vehicle capacities
    capacities = [100, 100, 100]
    
    # Location demands (depot has 0 demand)
    demands = [0, 10, 15, 20, 25, 30, 35, 40, 5, 10]
    
    # Initialize the optimizer with 3 vehicles
    optimizer = LogisticsRouteOptimizer(num_vehicles=3)
    
    # Create distance matrix
    distance_matrix = optimizer.create_distance_matrix(locations)
    
    print("\nOptimizing routes for 10 locations with 3 vehicles...")
    
    # Optimize routes
    routes, total_distance = optimizer.optimize_routes(
        distance_matrix,
        vehicle_capacities=capacities,
        demands=demands,
        max_route_distance=1000
    )
    
    # Print solution
    location_names = ['Depot'] + [f'Location {i}' for i in range(1, len(locations))]
    print("\nOptimized Routes:")
    optimizer.print_solution(routes, total_distance, location_names)
    
    # Calculate costs
    finance = LogisticsFinanceAnalyzer()
    route_costs, total_cost, cost_breakdown = finance.calculate_route_costs(
        routes, distance_matrix, cost_per_mile=2.5, fixed_cost_per_vehicle=150
    )
    
    print("\nCost Analysis:")
    print(f"Total cost: ${total_cost:.2f}")
    print("\nCost breakdown:")
    for cost_type, amount in cost_breakdown.items():
        print(f"  {cost_type}: ${amount:.2f}")
    
    # Visualize the solution
    visualize_routes(locations, routes)
    
    return routes, total_distance, cost_breakdown

def visualize_routes(locations, routes):
    """
    Visualize the optimized routes.
    
    Args:
        locations: List of (x, y) coordinates
        routes: List of routes (each route is a list of location indices)
    """
    try:
        # Convert locations to NumPy array for easier manipulation
        locations_array = np.array(locations)
        
        # Create a new figure
        plt.figure(figsize=(10, 8))
        
        # Plot all locations
        plt.scatter(
            locations_array[:, 0], 
            locations_array[:, 1], 
            c='lightgray', 
            s=100, 
            zorder=1
        )
        
        # Highlight the depot
        plt.scatter(
            locations_array[0, 0], 
            locations_array[0, 1], 
            c='red', 
            s=200, 
            marker='*', 
            label='Depot', 
            zorder=2
        )
        
        # Colors for different routes
        colors = ['blue', 'green', 'purple', 'orange', 'brown']
        
        # Plot each route
        for i, route in enumerate(routes):
            route_color = colors[i % len(colors)]
            
            # Extract coordinates for this route
            route_x = [locations[node][0] for node in route]
            route_y = [locations[node][1] for node in route]
            
            # Plot the route
            plt.plot(
                route_x, 
                route_y, 
                c=route_color, 
                linewidth=2, 
                label=f'Vehicle {i+1}', 
                zorder=1
            )
            
            # Plot the route direction with arrows
            for j in range(len(route) - 1):
                # Get coordinates
                x1, y1 = locations[route[j]]
                x2, y2 = locations[route[j+1]]
                
                # Calculate arrow position (middle of the line)
                arrow_x = (x1 + x2) / 2
                arrow_y = (y1 + y2) / 2
                
                # Calculate arrow direction
                dx = x2 - x1
                dy = y2 - y1
                
                # Add arrow
                plt.arrow(
                    arrow_x - dx * 0.1, 
                    arrow_y - dy * 0.1, 
                    dx * 0.2, 
                    dy * 0.2, 
                    head_width=3, 
                    head_length=3, 
                    fc=route_color, 
                    ec=route_color, 
                    zorder=3
                )
        
        # Add labels to locations
        for i, (x, y) in enumerate(locations):
            label = 'Depot' if i == 0 else f'{i}'
            plt.annotate(
                label, 
                (x, y), 
                xytext=(5, 5), 
                textcoords='offset points',
                fontsize=10
            )
        
        # Set labels and title
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.title('Optimized Delivery Routes')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        
        # Display the plot
        plt.tight_layout()
        plt.savefig('optimized_routes.png')  # Save the figure
        print("\nRoute visualization saved as 'optimized_routes.png'")
        plt.show()
        
    except Exception as e:
        print(f"Error visualizing routes: {e}")
        print("Route visualization skipped. Make sure matplotlib is installed.")

if __name__ == "__main__":
    run_example()
