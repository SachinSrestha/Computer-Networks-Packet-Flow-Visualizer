"""
Packet and PacketQueue classes for network simulation
"""

import time
import uuid
from typing import Optional, List, Any
from collections import deque
import numpy as np


class Packet:
    """Represents a network packet"""
    
    def __init__(self, source_id: str, destination_id: str, 
                 size: int = 1500, payload: Optional[Any] = None):
        """
        Initialize a packet
        
        Args:
            source_id: Source node ID
            destination_id: Destination node ID
            size: Packet size in bytes
            payload: Optional payload data
        """
        self.id = str(uuid.uuid4())[:8]
        self.source_id = source_id
        self.destination_id = destination_id
        self.size = size
        self.payload = payload or f"Data_{self.id}"
        
        # Routing information
        self.current_node_id: Optional[str] = source_id
        self.next_hop_id: Optional[str] = None
        self.path: List[str] = [source_id]  # Track the path taken
        
        # Timing information
        self.creation_time = time.time()
        self.delivery_time: Optional[float] = None
        self.hop_count = 0
        
        # Visual properties
        self.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.color = np.array([0.9, 0.5, 0.2, 1.0], dtype=np.float32)
        self.progress = 0.0  # Progress along current link (0.0 to 1.0)
        
        # State
        self.is_delivered = False
        self.is_dropped = False
        self.drop_reason: Optional[str] = None
    
    def advance_to_next_hop(self):
        """Move packet to the next hop"""
        if self.next_hop_id:
            self.current_node_id = self.next_hop_id
            self.path.append(self.next_hop_id)
            self.hop_count += 1
            self.next_hop_id = None
            self.progress = 0.0
    
    def mark_delivered(self):
        """Mark packet as delivered"""
        self.is_delivered = True
        self.delivery_time = time.time()
    
    def mark_dropped(self, reason: str = "Unknown"):
        """Mark packet as dropped"""
        self.is_dropped = True
        self.drop_reason = reason
        self.delivery_time = time.time()
    
    def get_latency(self) -> Optional[float]:
        """Get packet latency in milliseconds"""
        if self.delivery_time:
            return (self.delivery_time - self.creation_time) * 1000
        return None
    
    def __repr__(self):
        status = "delivered" if self.is_delivered else "dropped" if self.is_dropped else "in-flight"
        return f"Packet({self.id}, {self.source_id}->{self.destination_id}, {status})"


class PacketQueue:
    """FIFO queue for packets at a network node"""
    
    def __init__(self, max_size: int = 20):
        """
        Initialize a packet queue
        
        Args:
            max_size: Maximum number of packets in the queue
        """
        self.max_size = max_size
        self.queue: deque = deque(maxlen=max_size)
        
        # Statistics
        self.total_enqueued = 0
        self.total_dequeued = 0
        self.total_dropped = 0
    
    def enqueue(self, packet: Packet) -> bool:
        """
        Add a packet to the queue
        
        Args:
            packet: Packet to enqueue
            
        Returns:
            True if successful, False if queue is full
        """
        if len(self.queue) >= self.max_size:
            self.total_dropped += 1
            return False
        
        self.queue.append(packet)
        self.total_enqueued += 1
        return True
    
    def dequeue(self) -> Optional[Packet]:
        """
        Remove and return the first packet from the queue
        
        Returns:
            The packet, or None if queue is empty
        """
        if not self.queue:
            return None
        
        self.total_dequeued += 1
        return self.queue.popleft()
    
    def peek(self) -> Optional[Packet]:
        """
        View the first packet without removing it
        
        Returns:
            The packet, or None if queue is empty
        """
        return self.queue[0] if self.queue else None
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return len(self.queue) == 0
    
    def is_full(self) -> bool:
        """Check if queue is full"""
        return len(self.queue) >= self.max_size
    
    def size(self) -> int:
        """Get current queue size"""
        return len(self.queue)
    
    def clear(self):
        """Clear all packets from the queue"""
        self.queue.clear()
    
    def get_utilization(self) -> float:
        """Get queue utilization as a percentage"""
        return (len(self.queue) / self.max_size) * 100 if self.max_size > 0 else 0.0
    
    def __repr__(self):
        return f"PacketQueue(size={len(self.queue)}/{self.max_size})"
