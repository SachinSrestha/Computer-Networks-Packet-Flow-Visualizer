"""
Simulation engine for managing packet flow through the network
"""

import time
import random
from typing import List, Optional, Dict
import numpy as np

from core.network import Network, Node
from core.packet import Packet
from simulation.routing import RoutingAlgorithm, DijkstraRouting
import config


class SimulationEngine:
    """Manages the network simulation state and packet flow"""
    
    def __init__(self, network: Network, routing_algorithm: Optional[RoutingAlgorithm] = None):
        """
        Initialize the simulation engine
        
        Args:
            network: The network topology to simulate
            routing_algorithm: Routing algorithm to use (default: Dijkstra)
        """
        self.network = network
        self.routing_algorithm = routing_algorithm or DijkstraRouting(network)
        
        # Simulation state
        self.is_running = False
        self.simulation_time = 0.0
        self.simulation_speed = config.DEFAULT_SIMULATION_SPEED
        
        # Packet management
        self.active_packets: List[Packet] = []
        self.delivered_packets: List[Packet] = []
        self.dropped_packets: List[Packet] = []
        
        # Timing
        self.last_update_time = time.time()
        self.last_packet_generation_time = 0.0
        self.last_routing_update = 0.0  # Time of last routing update wait
        
        # Demonstration Mode
        self.auto_generate = True
        self.demo_packet_id: Optional[str] = None
        
        # Statistics
        self.total_packets_generated = 0
        self.average_latency = 0.0
        self.delivery_rate = 0.0
    
    def start(self):
        """Start the simulation"""
        self.is_running = True
        self.last_update_time = time.time()
    
    def pause(self):
        """Pause the simulation"""
        self.is_running = False
    
    def reset(self):
        """Reset the simulation to initial state"""
        self.is_running = False
        self.simulation_time = 0.0
        self.active_packets.clear()
        self.delivered_packets.clear()
        self.dropped_packets.clear()
        self.total_packets_generated = 0
        self.last_packet_generation_time = 0.0
        self.last_routing_update = 0.0
        self.auto_generate = True
        self.demo_packet_id = None
        
        # Clear all node queues
        for node in self.network.nodes.values():
            node.queue.clear()
            node.packets_sent = 0
            node.packets_received = 0
            node.packets_forwarded = 0
            node.packets_dropped = 0
        
        # Reset network statistics
        self.network.total_packets = 0
        self.network.delivered_packets = 0
        self.network.dropped_packets = 0
    
    def update(self, delta_time: float):
        """
        Update simulation state
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        if not self.is_running:
            return
        
        # Update simulation time
        self.simulation_time += delta_time * self.simulation_speed
        
        # Generate new packets periodically (if auto_generate is ON)
        if self.auto_generate:
            if (self.simulation_time - self.last_packet_generation_time >= 
                config.PACKET_GENERATION_INTERVAL):
                self.generate_random_packet()
                self.last_packet_generation_time = self.simulation_time
        
        # Check if demonstration packet is complete
        if self.demo_packet_id:
            # Check if it's still active
            is_active = any(p.id == self.demo_packet_id for p in self.active_packets)
            if not is_active:
                # Packet has been delivered or dropped
                self.auto_generate = True
                self.demo_packet_id = None
                print("Demonstration packet complete. Restoring normal traffic...")
        
        # Update all active packets
        self._update_packets(delta_time * self.simulation_speed)
        
        # Process queues at all nodes (limited throughput)
        for node in self.network.nodes.values():
            self._process_node_queue(node)
        
        # Update congestion states for all nodes
        self._update_congestion_states()
        
        # Periodically recalculate routing (every 0.5 seconds for faster adaptation)
        if self.simulation_time - self.last_routing_update >= 0.5:
            self.routing_algorithm.update_routing_tables()
            self.last_routing_update = self.simulation_time
        
        # Update statistics
        self._update_statistics()
    
    def generate_random_packet(self):
        """Generate a random packet between two nodes"""
        if len(self.network.nodes) < 2:
            return
        
        if len(self.active_packets) >= config.MAX_PACKETS_IN_FLIGHT:
            return
        
        # Select random source and destination
        node_ids = list(self.network.nodes.keys())
        source_id = random.choice(node_ids)
        destination_id = random.choice([nid for nid in node_ids if nid != source_id])
        
        self.generate_packet(source_id, destination_id)
    
    def generate_packet(self, source_id: str, destination_id: str):
        """
        Generate a packet from source to destination
        
        Args:
            source_id: Source node ID
            destination_id: Destination node ID
        """
        packet = Packet(source_id, destination_id, size=config.PACKET_SIZE)
        
        # Compute route using routing algorithm
        route = self.routing_algorithm.compute_route(source_id, destination_id)
        
        if not route or len(route) < 2:
            # No route available, drop packet
            packet.mark_dropped("No route available")
            self.dropped_packets.append(packet)
            return
        
        # Set next hop
        packet.next_hop_id = route[1]
        
        # Add to active packets
        self.active_packets.append(packet)
        self.total_packets_generated += 1
        self.network.total_packets += 1
        
        # Update source node
        source_node = self.network.get_node(source_id)
        if source_node:
            source_node.packets_sent += 1
            packet.position = source_node.position.copy()
            
        return packet
    
    def _update_packets(self, delta_time: float):
        """Update all active packets"""
        packets_to_remove = []
        
        for packet in self.active_packets:
            if packet.is_delivered:
                packets_to_remove.append(packet)
                continue
            
            if packet.is_dropped:
                # Keep dropped packets visible for 0.5s (visual feedback)
                if time.time() - packet.delivery_time > 0.5:
                    packets_to_remove.append(packet)
                continue
            
            # Update packet position and progress
            self._update_packet_movement(packet, delta_time)
            
            # Check if packet reached next hop
            if packet.progress >= 1.0:
                self._handle_packet_arrival(packet)
        
        # Remove completed packets
        for packet in packets_to_remove:
            self.active_packets.remove(packet)
            if packet.is_delivered:
                self.delivered_packets.append(packet)
                self.network.delivered_packets += 1
            else:
                self.dropped_packets.append(packet)
                self.network.dropped_packets += 1
    
    def _update_packet_movement(self, packet: Packet, delta_time: float):
        """Update packet position along its current link"""
        if not packet.next_hop_id:
            return
        
        # Get current and next node positions
        current_node = self.network.get_node(packet.current_node_id)
        next_node = self.network.get_node(packet.next_hop_id)
        
        if not current_node or not next_node:
            return
        
        # Get link to determine speed
        link = self.network.get_link_between(packet.current_node_id, packet.next_hop_id)
        if not link:
            return
        
        # Calculate movement speed based on link properties
        # Speed is inversely proportional to latency
        base_speed = 0.5  # Base speed units per second
        speed = base_speed / (link.latency / 10.0)  # Normalize by 10ms
        
        # Update progress
        packet.progress += speed * delta_time
        packet.progress = min(packet.progress, 1.0)
        
        # Interpolate position
        packet.position = (current_node.position * (1 - packet.progress) + 
                          next_node.position * packet.progress)
        
        # Mark link as active
        link.is_active = True
    
    def _handle_packet_arrival(self, packet: Packet):
        """
        Handle packet arrival at next hop
        Implements store-and-forward packet switching with queuing
        """
        # Move packet to next hop
        packet.advance_to_next_hop()
        
        current_node = self.network.get_node(packet.current_node_id)
        if not current_node:
            packet.mark_dropped("Node not found")
            return
        
        # Check if reached destination
        if packet.current_node_id == packet.destination_id:
            packet.mark_delivered()
            current_node.packets_received += 1
            return
        
        # Try to enqueue packet at intermediate node (store-and-forward)
        if not current_node.queue.enqueue(packet):
            # Queue is full - drop packet
            packet.mark_dropped(f"Queue full at node {current_node.id}")
            current_node.packets_dropped += 1
            return
        
        # Packet successfully queued (don't process immediately - let it wait)
        current_node.packets_forwarded += 1
    
    def _process_node_queue(self, node: Node):
        """
        Process packets in node's queue (very limited processing rate)
        Implements limited node processing capacity with significant delay
        """
        # Force Constant Congestion (New V-key Feature)
        if getattr(node, "force_congested", False):
            # Fill with dummy packets to ensure Red state
            while not node.queue.is_full():
                # We need Packet class. It is available in this file scope? 
                # Yes, engine imports Packet.
                dummy = Packet(f"BLOCK_{node.id}", node.id, "NOWHERE")
                node.queue.enqueue(dummy)
            
            node.update_congestion_state()
            # Do NOT process packets. Jam the node.
            return

        if node.queue.is_empty():
            return
        
        # Only process with 5% probability per frame (very restrictive - causes congestion)
        # This ensures queues build up significantly when traffic is high
        if random.random() > 0.05:
            return
        
        # Dequeue one packet for forwarding
        queued_packet = node.queue.dequeue()
        if not queued_packet:
            return
        
        # Compute next hop using current routing table
        route = self.routing_algorithm.compute_route(
            queued_packet.current_node_id,
            queued_packet.destination_id
        )
        
        if not route or len(route) < 2:
            # No route available - drop packet
            queued_packet.mark_dropped("No route from queued node")
            node.packets_dropped += 1
            return
        
        # Set next hop and send packet
        queued_packet.next_hop_id = route[1]
    
    def _update_congestion_states(self):
        """Update congestion state for all nodes based on queue size"""
        for node in self.network.nodes.values():
            node.update_congestion_state()
    
    def _update_statistics(self):
        """Update simulation statistics"""
        total_completed = len(self.delivered_packets) + len(self.dropped_packets)
        
        if total_completed > 0:
            self.delivery_rate = (len(self.delivered_packets) / total_completed) * 100
        
        if self.delivered_packets:
            latencies = [p.get_latency() for p in self.delivered_packets if p.get_latency()]
            self.average_latency = sum(latencies) / len(latencies) if latencies else 0.0
    
    def set_speed(self, speed: float):
        """Set simulation speed"""
        self.simulation_speed = max(config.MIN_SIMULATION_SPEED, 
                                   min(speed, config.MAX_SIMULATION_SPEED))
    
    def get_statistics(self) -> Dict:
        """Get current simulation statistics"""
        return {
            'total_generated': self.total_packets_generated,
            'active': len(self.active_packets),
            'delivered': len(self.delivered_packets),
            'dropped': len(self.dropped_packets),
            'delivery_rate': self.delivery_rate,
            'average_latency': self.average_latency,
            'simulation_time': self.simulation_time
        }
