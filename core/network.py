"""
Network topology components: Network, Node, and Link classes
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
import uuid


class Node:
    """Represents a network node (router, switch, or host)"""
    
    def __init__(self, node_id: str, position: Tuple[float, float, float], 
                 node_type: str = "router", name: Optional[str] = None):
        """
        Initialize a network node
        
        Args:
            node_id: Unique identifier for the node
            position: 3D position (x, y, z)
            node_type: Type of node (router, switch, host)
            name: Human-readable name
        """
        self.id = node_id
        self.position = np.array(position, dtype=np.float32)
        self.type = node_type
        self.name = name or f"{node_type}_{node_id}"
        
        # Network properties
        self.neighbors: List[str] = []  # List of neighbor node IDs
        self.routing_table: Dict[str, str] = {}  # destination -> next_hop
        
        # Packet queue
        from .packet import PacketQueue
        self.queue = PacketQueue(max_size=20)  # Fixed queue size
        
        # Visual properties
        self.base_color = np.array([0.2, 0.6, 0.9, 1.0], dtype=np.float32)
        self.color = self.base_color.copy()
        self.scale = 1.0
        self.is_active = False
        self.is_selected = False
        self.force_congested = False # If True, queue stays full
        
        # Congestion detection (threshold-based)
        self.congestion_state = "low"  # low, medium, high
        self.congestion_threshold_low = 3
        self.congestion_threshold_medium = 4
        self.congestion_threshold_high = 6
        
        # Statistics
        self.packets_sent = 0
        self.packets_received = 0
        self.packets_forwarded = 0
        self.packets_dropped = 0
    
    def add_neighbor(self, neighbor_id: str):
        """Add a neighbor to this node"""
        if neighbor_id not in self.neighbors:
            self.neighbors.append(neighbor_id)
    
    def remove_neighbor(self, neighbor_id: str):
        """Remove a neighbor from this node"""
        if neighbor_id in self.neighbors:
            self.neighbors.remove(neighbor_id)
    
    def update_routing_table(self, destination: str, next_hop: str):
        """Update routing table entry"""
        self.routing_table[destination] = next_hop
    
    def get_next_hop(self, destination: str) -> Optional[str]:
        """Get next hop for a destination"""
        return self.routing_table.get(destination)
    
    def update_congestion_state(self):
        """
        Update congestion state based on queue size
        Implements threshold-based congestion detection
        """
        queue_size = self.queue.size()
        
        if queue_size > self.congestion_threshold_high:
            self.congestion_state = "high"
            # Red color for high congestion
            self.color = np.array([0.9, 0.2, 0.2, 1.0], dtype=np.float32)
        elif queue_size >= self.congestion_threshold_medium:
            self.congestion_state = "medium"
            # Yellow color for medium congestion
            self.color = np.array([0.9, 0.8, 0.2, 1.0], dtype=np.float32)
        else:
            self.congestion_state = "low"
            # Green color for low traffic
            self.color = np.array([0.2, 0.8, 0.3, 1.0], dtype=np.float32)
    
    def get_congestion_cost(self) -> float:
        """
        Get dynamic congestion cost multiplier based on real-time queue occupancy.
        Returns a value from 1.0 (empty) to 10.0 (full).
        """
        if self.queue.max_size == 0:
            return 1.0
            
        # If node is forced congested, return max penalty immediately
        if getattr(self, "force_congested", False):
            return 10.0
            
        fill_ratio = self.queue.size() / self.queue.max_size
        # Cost increases linearly from 1x to 10x based on queue fill
        return 1.0 + (fill_ratio * 9.0)
    
    def __repr__(self):
        return f"Node({self.id}, {self.name}, pos={self.position})"


class Link:
    """Represents a network link between two nodes"""
    
    def __init__(self, link_id: str, source_id: str, target_id: str,
                 bandwidth: float = 100.0, latency: float = 10.0,
                 bidirectional: bool = True):
        """
        Initialize a network link
        
        Args:
            link_id: Unique identifier for the link
            source_id: Source node ID
            target_id: Target node ID
            bandwidth: Link bandwidth in Mbps
            latency: Link latency in ms
            bidirectional: Whether the link is bidirectional
        """
        self.id = link_id
        self.source_id = source_id
        self.target_id = target_id
        self.bandwidth = bandwidth  # Mbps
        self.latency = latency  # ms
        self.bidirectional = bidirectional
        
        # Link cost/weight for routing (delay-based)
        self.weight = latency  # Weight for shortest path calculation
        self.cost = latency    # Cost metric for routing
        
        # Visual properties
        self.color = np.array([0.4, 0.4, 0.5, 0.6], dtype=np.float32)
        self.width = 0.05
        self.is_active = False
        
        # Statistics
        self.packets_transmitted = 0
        self.bytes_transmitted = 0
        self.utilization = 0.0
    
    def get_endpoints(self) -> Tuple[str, str]:
        """Get the endpoint node IDs"""
        return self.source_id, self.target_id
    
    def contains_node(self, node_id: str) -> bool:
        """Check if the link connects to a specific node"""
        return node_id in (self.source_id, self.target_id)
    
    def get_other_end(self, node_id: str) -> Optional[str]:
        """Get the other endpoint given one endpoint"""
        if node_id == self.source_id:
            return self.target_id
        elif node_id == self.target_id and self.bidirectional:
            return self.source_id
        return None
    
    def __repr__(self):
        direction = "<->" if self.bidirectional else "->"
        return f"Link({self.id}, {self.source_id} {direction} {self.target_id})"


class Network:
    """Represents the entire network topology"""
    
    def __init__(self, name: str = "Network"):
        """
        Initialize a network
        
        Args:
            name: Name of the network
        """
        self.name = name
        self.nodes: Dict[str, Node] = {}
        self.links: Dict[str, Link] = {}
        
        # Network statistics
        self.total_packets = 0
        self.delivered_packets = 0
        self.dropped_packets = 0
    
    def add_node(self, node: Node) -> bool:
        """Add a node to the network"""
        if node.id in self.nodes:
            return False
        self.nodes[node.id] = node
        return True
    
    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the network"""
        if node_id not in self.nodes:
            return False
        
        # Remove all links connected to this node
        links_to_remove = [
            link_id for link_id, link in self.links.items()
            if link.contains_node(node_id)
        ]
        for link_id in links_to_remove:
            self.remove_link(link_id)
        
        del self.nodes[node_id]
        return True
    
    def add_link(self, link: Link) -> bool:
        """Add a link to the network"""
        if link.id in self.links:
            return False
        
        # Verify both endpoints exist
        if link.source_id not in self.nodes or link.target_id not in self.nodes:
            return False
        
        self.links[link.id] = link
        
        # Update node neighbors
        self.nodes[link.source_id].add_neighbor(link.target_id)
        if link.bidirectional:
            self.nodes[link.target_id].add_neighbor(link.source_id)
        
        return True
    
    def remove_link(self, link_id: str) -> bool:
        """Remove a link from the network"""
        if link_id not in self.links:
            return False
        
        link = self.links[link_id]
        
        # Update node neighbors
        if link.source_id in self.nodes:
            self.nodes[link.source_id].remove_neighbor(link.target_id)
        if link.bidirectional and link.target_id in self.nodes:
            self.nodes[link.target_id].remove_neighbor(link.source_id)
        
        del self.links[link_id]
        return True
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID"""
        return self.nodes.get(node_id)
    
    def get_link(self, link_id: str) -> Optional[Link]:
        """Get a link by ID"""
        return self.links.get(link_id)
    
    def get_link_between(self, source_id: str, target_id: str) -> Optional[Link]:
        """Get a link between two nodes"""
        for link in self.links.values():
            if link.source_id == source_id and link.target_id == target_id:
                return link
            if link.bidirectional and link.source_id == target_id and link.target_id == source_id:
                return link
        return None
    
    def get_neighbors(self, node_id: str) -> List[str]:
        """Get all neighbors of a node"""
        node = self.get_node(node_id)
        return node.neighbors if node else []
    
    def clear(self):
        """Clear all nodes and links"""
        self.nodes.clear()
        self.links.clear()
        self.total_packets = 0
        self.delivered_packets = 0
        self.dropped_packets = 0
    
    def __repr__(self):
        return f"Network({self.name}, nodes={len(self.nodes)}, links={len(self.links)})"
