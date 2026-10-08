
""

import heapq
from typing import Dict, List, Optional, Tuple

class PowerGrid:
    """Graph Data Structure representing physical infrastructure."""
    
    def __init__(self):
        # Adjacency list mapping: node -> {neighbor: weight}
        self._infrastructure: Dict[str, Dict[str, float]] = {}

    def add_substation(self, name: str) -> None:
        """Initializes a vertex in the grid."""
        if name not in self._infrastructure:
            self._infrastructure[name] = {}

    def add_transmission_line(self, node1: str, node2: str, constraint_weight: float) -> None:
        """Maps a bidirectional edge with a specific routing constraint."""
        self.add_substation(node1)
        self.add_substation(node2)
        self._infrastructure[node1][node2] = constraint_weight
        self._infrastructure[node2][node1] = constraint_weight

    def simulate_line_failure(self, node1: str, node2: str) -> None:
        """Models physical damage by purposely omitting specific edges."""
        if node2 in self._infrastructure.get(node1, {}):
            del self._infrastructure[node1][node2]
        if node1 in self._infrastructure.get(node2, {}):
            del self._infrastructure[node2][node1]
            
    def get_neighbors(self, node: str) -> Dict[str, float]:
        return self._infrastructure.get(node, {})
        
    def get_all_nodes(self) -> List[str]:
        return list(self._infrastructure.keys())


class RestorationRouter:
    """Core Logic & Extraction Module for Pathfinding."""
    
    @staticmethod
    def calculate_optimal_route(grid: PowerGrid, source: str, target: str) -> Tuple[Optional[List[str]], float]:
        """
        Executes Dijkstra's algorithm. Returns a tuple of (Route_List, Total_Cost).
        Returns (None, infinity) if the target is completely isolated.
        """
        nodes = grid.get_all_nodes()
        if source not in nodes or target not in nodes:
            raise ValueError("Source or target substation does not exist in the grid.")

        # Phase 1: State Initialization
        distances = {node: float('infinity') for node in nodes}
        distances[source] = 0.0
        predecessors = {node: None for node in nodes}
        
        # Priority Queue: (accumulated_weight, current_node)
        pq = [(0.0, source)]

        while pq:
            current_cost, current_node = heapq.heappop(pq)

            # Optimization: Early exit if destination is reached
            if current_node == target:
                break

            if current_cost > distances[current_node]:
                continue

            # Phase 2: Edge Relaxation
            for neighbor, weight in grid.get_neighbors(current_node).items():
                new_cost = current_cost + weight
                
                if new_cost < distances[neighbor]:
                    distances[neighbor] = new_cost
                    predecessors[neighbor] = current_node
                    heapq.heappush(pq, (new_cost, neighbor))

        # Failsafe Logic: Handling Complete Isolation
        if distances[target] == float('infinity'):
            return None, float('infinity')

        # Step 3: Path Tracing & Extraction
        path = []
        current = target
        while current is not None:
            path.append(current)
            current = predecessors[current]
            
        return path[::-1], distances[target]


# --- System Execution & Simulation Testing ---
if __name__ == "__main__":
    # 1. Initialize the modular system
    regional_grid = PowerGrid()
    
    # 2. Build standard infrastructure
    regional_grid.add_transmission_line('Source_Plant', 'Substation_A', 10)
    regional_grid.add_transmission_line('Source_Plant', 'Substation_B', 50)
    regional_grid.add_transmission_line('Substation_A', 'Substation_B', 20)
    regional_grid.add_transmission_line('Substation_A', 'Substation_C', 30)
    regional_grid.add_transmission_line('Substation_C', 'Hospital', 40)
    regional_grid.add_transmission_line('Substation_B', 'Hospital', 150)
    regional_grid.add_substation('Isolated_Zone') # Completely disconnected
    
    # 3. Validation: Optimal Multi-Hop Route
    route, cost = RestorationRouter.calculate_optimal_route(regional_grid, 'Source_Plant', 'Hospital')
    print(f"Optimal Route: {' -> '.join(route)} | Total Cost: {cost}")
    
    # 4. Validation: Simulating Physical Damage (Dynamic Re-routing)
    print("\n[ALERT] Lightning strike detected. Transmission line A <-> C severed.")
    regional_grid.simulate_line_failure('Substation_A', 'Substation_C')
    
    reroute, new_cost = RestorationRouter.calculate_optimal_route(regional_grid, 'Source_Plant', 'Hospital')
    print(f"Reroute Required: {' -> '.join(reroute)} | New Cost: {new_cost}")
    
    # 5. Validation: Complete Isolation Failsafe
    print("\n[ALERT] Attempting to route to unmapped territory...")
    iso_route, iso_cost = RestorationRouter.calculate_optimal_route(regional_grid, 'Source_Plant', 'Isolated_Zone')
    if not iso_route:
        print(f"Failsafe Triggered: Target cannot be restored. Status: Isolated (Cost: {iso_cost})")