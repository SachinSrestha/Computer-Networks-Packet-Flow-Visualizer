"""
Routing algorithms for network packet forwarding
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import heapq
from collections import deque

from core.network import Network


class RoutingAlgorithm(ABC):
    """Abstract base class for routing algorithms"""
    
    def __init__(self, network: Network):
        """
        Initialize routing algorithm
        
        Args:
            network: The network topology
        """
        self.network = network
    
    @abstractmethod
    def compute_route(self, source_id: str, destination_id: str) -> Optional[List[str]]:
        """
        Compute route from source to destination
        
        Args:
            source_id: Source node ID
            destination_id: Destination node ID
            
        Returns:
            List of node IDs representing the path, or None if no path exists
        """
        pass
    
    @abstractmethod
    def update_routing_tables(self):
        """Update routing tables for all nodes in the network"""
        pass


class DijkstraRouting(RoutingAlgorithm):
    """Dijkstra's shortest path routing algorithm"""
    
    def compute_route(self, source_id: str, destination_id: str) -> Optional[List[str]]:
        """
        Compute shortest path using Dijkstra's algorithm
        
        Args:
            source_id: Source node ID
            destination_id: Destination node ID
            
        Returns:
            List of node IDs representing the shortest path
        """
        if source_id not in self.network.nodes or destination_id not in self.network.nodes:
            return None
        
        if source_id == destination_id:
            return [source_id]
        
        # Initialize distances and previous nodes
        distances: Dict[str, float] = {node_id: float('inf') for node_id in self.network.nodes}
        distances[source_id] = 0
        previous: Dict[str, Optional[str]] = {node_id: None for node_id in self.network.nodes}
        
        # Priority queue: (distance, node_id)
        pq = [(0, source_id)]
        visited = set()
        
        while pq:
            current_dist, current_id = heapq.heappop(pq)
            
            if current_id in visited:
                continue
            
            visited.add(current_id)
            
            if current_id == destination_id:
                break
            
            # Check all neighbors
            current_node = self.network.get_node(current_id)
            if not current_node:
                continue
            
            for neighbor_id in current_node.neighbors:
                if neighbor_id in visited:
                    continue
                
                # Get link cost (latency + congestion penalty for adaptive routing)
                link = self.network.get_link_between(current_id, neighbor_id)
                if not link:
                    continue
                
                # Calculate adaptive cost: link weight + neighbor congestion cost
                neighbor_node = self.network.get_node(neighbor_id)
                link_cost = link.weight if hasattr(link, 'weight') else link.latency
                
                # Add congestion penalty for adaptive routing
                congestion_multiplier = 1.0
                if neighbor_node:
                    # HEURISTIC: Use a massive penalty for forced congestion to ensure absolute rerouting
                    if getattr(neighbor_node, 'force_congested', False):
                        congestion_multiplier = 99.0 # 99x cost for forced nodes
                    else:
                        congestion_multiplier = neighbor_node.get_congestion_cost()
                
                # Final cost = base link cost * congestion multiplier
                cost = link_cost * congestion_multiplier
                new_distance = current_dist + cost
                
                if new_distance < distances[neighbor_id]:
                    distances[neighbor_id] = new_distance
                    previous[neighbor_id] = current_id
                    heapq.heappush(pq, (new_distance, neighbor_id))
        
        # Reconstruct path
        if distances[destination_id] == float('inf'):
            return None  # No path exists
        
        path = []
        current = destination_id
        while current is not None:
            path.append(current)
            current = previous[current]
        
        path.reverse()
        return path
    
    def update_routing_tables(self):
        """Update routing tables for all nodes using Dijkstra's algorithm"""
        for source_id in self.network.nodes:
            for dest_id in self.network.nodes:
                if source_id == dest_id:
                    continue
                
                route = self.compute_route(source_id, dest_id)
                if route and len(route) >= 2:
                    next_hop = route[1]
                    self.network.nodes[source_id].update_routing_table(dest_id, next_hop)


class FloodingRouting(RoutingAlgorithm):
    """Simple flooding routing algorithm (broadcasts to all neighbors)"""
    
    def compute_route(self, source_id: str, destination_id: str) -> Optional[List[str]]:
        """
        Compute route using BFS (flooding simulation)
        
        Args:
            source_id: Source node ID
            destination_id: Destination node ID
            
        Returns:
            List of node IDs representing a path
        """
        if source_id not in self.network.nodes or destination_id not in self.network.nodes:
            return None
        
        if source_id == destination_id:
            return [source_id]
        
        # BFS to find any path
        queue = deque([(source_id, [source_id])])
        visited = {source_id}
        
        while queue:
            current_id, path = queue.popleft()
            
            current_node = self.network.get_node(current_id)
            if not current_node:
                continue
            
            for neighbor_id in current_node.neighbors:
                if neighbor_id in visited:
                    continue
                
                new_path = path + [neighbor_id]
                
                if neighbor_id == destination_id:
                    return new_path
                
                visited.add(neighbor_id)
                queue.append((neighbor_id, new_path))
        
        return None  # No path exists
    
    def update_routing_tables(self):
        """Update routing tables using flooding approach"""
        for source_id in self.network.nodes:
            for dest_id in self.network.nodes:
                if source_id == dest_id:
                    continue
                
                route = self.compute_route(source_id, dest_id)
                if route and len(route) >= 2:
                    next_hop = route[1]
                    self.network.nodes[source_id].update_routing_table(dest_id, next_hop)
