"""
OpenGL renderer for 2D network visualization
"""

import numpy as np
import math
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from typing import List, Tuple, Optional

from core.network import Network, Node, Link
from core.packet import Packet
import config


class Renderer:
    """OpenGL 2D renderer for network visualization"""
    
    def __init__(self, width: int, height: int):
        """
        Initialize the renderer
        
        Args:
            width: Window width
            height: Window height
        """
        self.width = width
        self.height = height
        
        # Camera properties for 2D (pan and zoom)
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.zoom = 50.0  # Pixels per unit
        
        # Mouse interaction
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.is_panning = False
        self.dragged_node_id: Optional[str] = None
        
        # Node selection
        self.selected_node_id = None
        
        # Initialize OpenGL
        self._init_opengl()
    
    def _init_opengl(self):
        """Initialize OpenGL settings for 2D"""
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
        
        # Set background color
        glClearColor(*config.BACKGROUND_COLOR)
    
    def resize(self, width: int, height: int):
        """Handle window resize"""
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)
    
    def setup_camera(self):
        """Setup 2D orthographic projection"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        # Calculate view bounds based on zoom and window size
        half_width = (self.width / 2.0) / self.zoom
        half_height = (self.height / 2.0) / self.zoom
        
        # Orthographic projection for 2D
        glOrtho(
            self.camera_x - half_width, self.camera_x + half_width,
            self.camera_y - half_height, self.camera_y + half_height,
            -1.0, 1.0
        )
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
    def render(self, network: Network, packets: List[Packet], stats: dict = None):
        """
        Render the network and packets in 2D
        
        Args:
            network: Network to render
            packets: List of active packets
            stats: Optional statistics dictionary
        """
        glClear(GL_COLOR_BUFFER_BIT)
        
        self.setup_camera()
        
        # Draw grid
        self._draw_grid()
        
        # Draw links (behind nodes)
        for link in network.links.values():
            self._draw_link(link, network)
        
        # Draw nodes
        for node in network.nodes.values():
            self._draw_node(node)
        
        # Draw packets (on top)
        for packet in packets:
            self._draw_packet(packet, network)
        
        # Draw statistics panel (in screen space)
        if stats:
            self._draw_stats_panel(stats, network)
        
        # Draw selected node info
        if self.selected_node_id:
            self._draw_node_info(network)
    
    def _draw_grid(self):
        """Draw reference grid in 2D"""
        glColor4f(0.2, 0.2, 0.25, 0.3)
        glLineWidth(1.0)
        
        size = config.GRID_SIZE
        spacing = config.GRID_SPACING
        
        glBegin(GL_LINES)
        for i in range(-size, size + 1):
            # Horizontal lines
            glVertex2f(-size * spacing, i * spacing)
            glVertex2f(size * spacing, i * spacing)
            # Vertical lines
            glVertex2f(i * spacing, -size * spacing)
            glVertex2f(i * spacing, size * spacing)
        glEnd()
    
    def _draw_node(self, node: Node):
        """Draw a network node as a filled circle in 2D"""
        # Set color based on state
        # Determine node color based on congestion (priority)
        color = node.color
        
        # Use X and Z coordinates for 2D (ignore Y)
        x = node.position[0]
        y = node.position[2]
        radius = config.NODE_RADIUS * node.scale
        
        # Draw filled circle
        glColor4fv(color)
        self._draw_filled_circle(x, y, radius, 32)
        
        # Draw outline
        if node.is_selected:
            # Thick bright outline for selected node
            glColor4f(1.0, 1.0, 1.0, 1.0)
            glLineWidth(3.0)
            self._draw_circle_outline(x, y, radius * 1.1, 32)
        elif node.is_active:
             # Active outline
            glColor4f(1.0, 0.8, 0.4, 0.8)
            glLineWidth(2.0)
            self._draw_circle_outline(x, y, radius * 1.05, 32)
        else:
            # Normal outline
            glColor4f(1.0, 1.0, 1.0, 0.5)
            glLineWidth(2.0)
            self._draw_circle_outline(x, y, radius, 32)
        
        # Draw Visual Queue (Stack of packets)
        self._draw_node_queue_visuals(node, x, y, radius)
        
        # Draw Node ID Label
        # Calculate dynamic offset to center text based on zoom
        # Estimate: 4 pixels per char width, 4 pixels for half-height
        text_w_offset = (len(node.id) * 4.0) / self.zoom
        text_h_offset = 4.0 / self.zoom
        self._render_text(x - text_w_offset, y - text_h_offset, node.id, (1.0, 1.0, 1.0, 1.0))
        
        # Reset active state
        node.is_active = False
    
    def _draw_node_queue_visuals(self, node: Node, x: float, y: float, radius: float):
        """Draw a stack of small squares representing queued packets"""
        queue_size = node.queue.size()
        if queue_size == 0:
            return
            
        pkt_size = 0.15
        gap = 0.05
        
        # Start drawing to the top-right of the node
        start_x = x + radius + 0.1
        start_y = y - (queue_size * (pkt_size + gap)) / 2.0
        
        # Draw a small square for each queued packet
        for i in range(queue_size):
            # Color gradient based on position in queue (Oldest = Redder, Newest = Greener? Or uniform)
            # uniformity is cleaner. Use Congestion color or White?
            # Let's use White to contrast with background
            glColor4f(1.0, 1.0, 1.0, 0.9)
            
            py = start_y + i * (pkt_size + gap)
            
            glBegin(GL_QUADS)
            glVertex2f(start_x, py)
            glVertex2f(start_x + pkt_size, py)
            glVertex2f(start_x + pkt_size, py + pkt_size)
            glVertex2f(start_x, py + pkt_size)
            glEnd()
    
    def _draw_filled_circle(self, x: float, y: float, radius: float, segments: int):
        """Draw a filled circle"""
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(x, y)  # Center
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            dx = radius * math.cos(angle)
            dy = radius * math.sin(angle)
            glVertex2f(x + dx, y + dy)
        glEnd()
    
    def _draw_circle_outline(self, x: float, y: float, radius: float, segments: int):
        """Draw a circle outline"""
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            dx = radius * math.cos(angle)
            dy = radius * math.sin(angle)
            glVertex2f(x + dx, y + dy)
        glEnd()
    
    def _draw_link(self, link: Link, network: Network):
        """Draw a network link as a line in 2D"""
        source = network.get_node(link.source_id)
        target = network.get_node(link.target_id)
        
        if not source or not target:
            return
        
        # Set color based on state
        color = config.LINK_COLOR_ACTIVE if link.is_active else link.color
        glColor4fv(color)
        
        glLineWidth(link.width * 100)
        
        # Use X and Z coordinates for 2D
        glBegin(GL_LINES)
        glVertex2f(source.position[0], source.position[2])
        glVertex2f(target.position[0], target.position[2])
        glEnd()
        
        # Draw Link Cost Text
        # Midpoint
        mx = (source.position[0] + target.position[0]) / 2
        my = (source.position[2] + target.position[2]) / 2
        
        # Calculate dynamic cost
        cost = link.latency * target.get_congestion_cost()
        text = f"Cost: {cost:.1f}"
        
        self._render_text(mx, my + 0.2, text, (0.7, 0.7, 0.7, 1.0))
        
        # Reset active state
        link.is_active = False
    
    def _draw_packet(self, packet: Packet, network: Network):
        """Draw a packet as a directional triangle/arrow"""
        if packet.is_dropped:
            self._draw_dropped_packet(packet)
            return

        glColor4fv(packet.color)
        
        # Use X and Z coordinates for 2D
        x = packet.position[0]
        y = packet.position[2]
        size = config.PACKET_SIZE_VISUAL
        
        # Calculate rotation
        angle = 0.0
        if packet.current_node_id and packet.next_hop_id:
            curr_node = network.get_node(packet.current_node_id)
            next_node = network.get_node(packet.next_hop_id)
            if curr_node and next_node:
                dx = next_node.position[0] - curr_node.position[0]
                dy = next_node.position[2] - curr_node.position[2]
                angle = math.degrees(math.atan2(dy, dx))
        
        glPushMatrix()
        glTranslatef(x, y, 0.0)
        glRotatef(angle, 0.0, 0.0, 1.0) # Rotate around Z axis (Screen plane rotation)
        
        # Draw Arrow/Triangle pointing RIGHT (0 degrees)
        glBegin(GL_TRIANGLES)
        glVertex2f(size, 0.0)           # Tip
        glVertex2f(-size, size * 0.6)   # Back Left
        glVertex2f(-size, -size * 0.6)  # Back Right
        glEnd()
        
        glPopMatrix()
        
    def _draw_dropped_packet(self, packet: Packet):
        """Draw dropped packet as a fading red X"""
        # Calculate fade
        if packet.delivery_time:
            age = time.time() - packet.delivery_time
            alpha = max(0.0, 1.0 - (age / 0.5))
        else:
            alpha = 1.0
            
        glColor4f(1.0, 1.0, 1.0, alpha)
        
        x = packet.position[0]
        y = packet.position[2]
        size = config.PACKET_SIZE_VISUAL * 1.5
        
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex2f(x - size, y - size)
        glVertex2f(x + size, y + size)
        glVertex2f(x - size, y + size)
        glVertex2f(x + size, y - size)
        glEnd()
        
        # Draw outline for visibility
        glColor4f(1.0, 1.0, 1.0, 0.8)
        glLineWidth(1.5)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x - size, y - size)
        glVertex2f(x + size, y - size)
        glVertex2f(x + size, y + size)
        glVertex2f(x - size, y + size)
        glEnd()
    
    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates"""
        world_x = self.camera_x + (screen_x - self.width / 2.0) / self.zoom
        # Y is inverted (Screen Y increases down, World Y increases up?) 
        # Wait, checking glOrtho. Top is camera_y + half. 
        # So screen Y=0 (top) maps to camera_y + half. Screen Y=Height (bottom) maps to camera_y - half.
        # Logic: (screen_y - half_h) is +ve at bottom.
        # But we want World Y. 
        # Existing logic was: self.camera_y - (screen_y - self.height/2.0) / zoom
        # Let's keep existing logic.
        world_y = self.camera_y - (screen_y - self.height / 2.0) / self.zoom
        return world_x, world_y

    def handle_mouse_button(self, button: int, action: int, x: float, y: float, network: Network = None):
        """
        Handle mouse button events
        Args:
            network: Required to check for node hits if dragged
        """
        if button == 0:  # Left button
            if action == 1:  # Press
                self.last_mouse_x = x
                self.last_mouse_y = y
                
                # Check if we clicked a node (using current selection state which main.py updates before calling this)
                # But safer to check again or rely on state.
                # If selected_node_id is set, and we clicked ON it, start drag.
                # But select_node_at updates selected_node_id.
                
                if self.selected_node_id:
                     # Verify click is actually on the node (select_node_at does this)
                     # So if main.py called select_node_at, selected_node_id is valid for this click.
                     self.dragged_node_id = self.selected_node_id
                     self.is_panning = False
                else:
                     self.is_panning = True
                     self.dragged_node_id = None
                     
            else:  # Release
                self.is_panning = False
                self.dragged_node_id = None

    def handle_mouse_move(self, x: float, y: float, network: Network = None):
        """Handle mouse movement for panning or dragging nodes"""
        dx = x - self.last_mouse_x
        dy = y - self.last_mouse_y
        
        if self.is_panning:
            # Pan the camera (inverted for natural feel)
            self.camera_x -= dx / self.zoom
            self.camera_y += dy / self.zoom
            
        elif self.dragged_node_id and network:
            # Move the node
            node = network.get_node(self.dragged_node_id)
            if node:
                # Calculate movement in world units
                world_dx = dx / self.zoom
                # World Y is inverted relative to screen dy?
                # screen_to_world logic: world_y = CamY - (ScreenY...)/Zoom.
                # Delta World Y = - Delta Screen Y / Zoom.
                world_dy = -dy / self.zoom
                
                node.position[0] += world_dx
                node.position[2] += world_dy
                
        self.last_mouse_x = x
        self.last_mouse_y = y
    
    def select_node_at(self, screen_x: float, screen_y: float, network: Network) -> Optional[str]:
        """
        Select a node at the given screen coordinates
        
        Args:
            screen_x: Mouse X coordinate in screen space
            screen_y: Mouse Y coordinate in screen space
            network: Network containing nodes
            
        Returns:
            ID of selected node, or None
        """
        # Convert screen coordinates to world coordinates
        world_x, world_y = self.screen_to_world(screen_x, screen_y)
        
        # Find closest node within selection radius
        min_distance = float('inf')
        selected_id = None
        selection_radius = 0.5  # World units
        
        for node in network.nodes.values():
            # Use X and Z coordinates for 2D
            node_x = node.position[0]
            node_y = node.position[2]
            
            # Calculate distance
            dx = world_x - node_x
            dy = world_y - node_y
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance < selection_radius and distance < min_distance:
                min_distance = distance
                selected_id = node.id
        
        # Update selection state
        for node in network.nodes.values():
            node.is_selected = (node.id == selected_id)
        
        self.selected_node_id = selected_id
        return selected_id
    
        # Restore matrices
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def _render_text(self, x: float, y: float, text: str, color: tuple):
        """Render text using GLUT bitmap fonts"""
        try:
            glColor4fv(color)
            glRasterPos2f(x, y)
            for char in text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
        except Exception as e:
            pass  # Fallback or ignore if GLUT fails
            
    def _draw_stats_panel(self, stats: dict, network: Network):
        """Draw statistics panel with clear text labels and per-node queue info"""
        # Switch to screen space
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Calculate dynamic height based on node count
        node_count = len(network.nodes)
        base_height = 280
        per_node_height = 20
        panel_height = base_height + (node_count * per_node_height)
        
        panel_x = 10
        panel_y = 10
        panel_width = 300
        
        # Background
        glColor4f(0.1, 0.1, 0.15, 0.9)
        glBegin(GL_QUADS)
        glVertex2f(panel_x, panel_y)
        glVertex2f(panel_x + panel_width, panel_y)
        glVertex2f(panel_x + panel_width, panel_y + panel_height)
        glVertex2f(panel_x, panel_y + panel_height)
        glEnd()
        
        # Border
        glColor4f(0.3, 0.5, 0.7, 1.0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(panel_x, panel_y)
        glVertex2f(panel_x + panel_width, panel_y)
        glVertex2f(panel_x + panel_width, panel_y + panel_height)
        glVertex2f(panel_x, panel_y + panel_height)
        glEnd()
        
        # Title
        self._render_text(panel_x + 15, panel_y + 20, "NETWORK STATISTICS", (1.0, 1.0, 1.0, 1.0))
        
        y_pos = panel_y + 50
        line_height = 25
        
        # Helper to draw row
        def draw_stat_row(label, value, value_color):
            self._render_text(panel_x + 15, y_pos, label, (0.8, 0.8, 0.8, 1.0))
            self._render_text(panel_x + 130, y_pos, str(value), value_color)
        
        draw_stat_row("Generated:", stats.get('total_generated', 0), (0.3, 0.7, 0.9, 1.0))
        y_pos += line_height
        
        draw_stat_row("Delivered:", stats.get('delivered', 0), (0.2, 0.8, 0.3, 1.0))
        y_pos += line_height
        
        draw_stat_row("Dropped:", stats.get('dropped', 0), (0.9, 0.3, 0.2, 1.0))
        y_pos += line_height
        
        draw_stat_row("Active:", stats.get('active', 0), (0.9, 0.7, 0.2, 1.0))
        y_pos += line_height
        
        # Delivery Rate
        rate = stats.get('delivery_rate', 0)
        self._render_text(panel_x + 15, y_pos, "Delivery Rate:", (0.8, 0.8, 0.8, 1.0))
        self._render_text(panel_x + 130, y_pos, f"{rate:.1f}%", (0.3, 0.9, 0.5, 1.0))
        y_pos += line_height
        
        # Congestion Summary
        y_pos += 10
        self._render_text(panel_x + 15, y_pos, "Congestion Levels:", (1.0, 1.0, 1.0, 1.0))
        y_pos += 20
        
        counts = {"low": 0, "medium": 0, "high": 0}
        for node in network.nodes.values():
            counts[node.congestion_state] += 1
            
        self._render_text(panel_x + 15, y_pos, f"Low: {counts['low']}", (0.2, 0.8, 0.3, 1.0))
        self._render_text(panel_x + 100, y_pos, f"Med: {counts['medium']}", (0.9, 0.8, 0.2, 1.0))
        self._render_text(panel_x + 185, y_pos, f"High: {counts['high']}", (0.9, 0.2, 0.2, 1.0))
        
        # Per-Node Queue List
        y_pos += 30
        self._render_text(panel_x + 15, y_pos, "NODE QUEUES:", (1.0, 1.0, 1.0, 1.0))
        y_pos += 20
        
        # Sort nodes by ID for consistent display
        sorted_nodes = sorted(network.nodes.values(), key=lambda n: n.id)
        
        for node in sorted_nodes:
            # Node ID
            self._render_text(panel_x + 15, y_pos, f"Node {node.id}:", (0.9, 0.9, 0.9, 1.0))
            
            # Queue Value
            q_size = node.queue.size()
            q_max = node.queue.max_size
            
            # Color based on fill
            if q_size > 6: q_color = (0.9, 0.3, 0.2, 1.0) # Red
            elif q_size > 3: q_color = (0.9, 0.8, 0.2, 1.0) # Yellow
            else: q_color = (0.2, 0.8, 0.3, 1.0) # Green
            
            self._render_text(panel_x + 80, y_pos, f"{q_size}/{q_max}", q_color)
            
            # Visual Bar background
            bar_x = panel_x + 130
            bar_w = 100
            bar_h = 10
            
            glColor4f(0.3, 0.3, 0.3, 0.5)
            glBegin(GL_QUADS)
            glVertex2f(bar_x, y_pos - 8)
            glVertex2f(bar_x + bar_w, y_pos - 8)
            glVertex2f(bar_x + bar_w, y_pos - 8 + bar_h)
            glVertex2f(bar_x, y_pos - 8 + bar_h)
            glEnd()
            
            # Visual Bar fill
            fill_w = (q_size / q_max) * bar_w
            glColor4fv(q_color)
            glBegin(GL_QUADS)
            glVertex2f(bar_x, y_pos - 8)
            glVertex2f(bar_x + fill_w, y_pos - 8)
            glVertex2f(bar_x + fill_w, y_pos - 8 + bar_h)
            glVertex2f(bar_x, y_pos - 8 + bar_h)
            glEnd()
            
            y_pos += 20

        # Restore matrices
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def _draw_node_info(self, network: Network):
        """Draw selected node information using text"""
        node = network.get_node(self.selected_node_id)
        if not node:
            return
            
        # Switch to screen space
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Calculate dynamic panel height for routing table
        rt_count = len(node.routing_table)
        base_height = 180
        rt_height = 30 + (rt_count * 20) if rt_count > 0 else 20
        panel_height = base_height + rt_height
        
        panel_width = 300
        panel_x = self.width - panel_width - 10
        panel_y = 10
        
        # Background
        glColor4f(0.1, 0.1, 0.15, 0.9)
        glBegin(GL_QUADS)
        glVertex2f(panel_x, panel_y)
        glVertex2f(panel_x + panel_width, panel_y)
        glVertex2f(panel_x + panel_width, panel_y + panel_height)
        glVertex2f(panel_x, panel_y + panel_height)
        glEnd()
        
        # Border
        glColor4f(0.3, 0.9, 0.5, 1.0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(panel_x, panel_y)
        glVertex2f(panel_x + panel_width, panel_y)
        glVertex2f(panel_x + panel_width, panel_y + panel_height)
        glVertex2f(panel_x, panel_y + panel_height)
        glEnd()
        
        # Content
        self._render_text(panel_x + 15, panel_y + 20, f"NODE DETAILS: {node.id}", (1.0, 1.0, 1.0, 1.0))
        
        y_pos = panel_y + 50
        line_height = 25
        
        # Stats
        self._render_text(panel_x + 15, y_pos, "Queue:", (0.8, 0.8, 0.8, 1.0))
        queue_color = (0.2, 0.8, 0.3, 1.0)
        if node.queue.size() > 5: queue_color = (0.9, 0.8, 0.2, 1.0)
        if node.queue.size() > 10: queue_color = (0.9, 0.2, 0.2, 1.0)
        self._render_text(panel_x + 130, y_pos, f"{node.queue.size()} / {node.queue.max_size}", queue_color)
        y_pos += line_height
        
        self._render_text(panel_x + 15, y_pos, "State:", (0.8, 0.8, 0.8, 1.0))
        state_color = (0.2, 0.8, 0.3, 1.0)
        if node.congestion_state == "medium": state_color = (0.9, 0.8, 0.2, 1.0)
        if node.congestion_state == "high": state_color = (0.9, 0.2, 0.2, 1.0)
        self._render_text(panel_x + 130, y_pos, node.congestion_state.upper(), state_color)
        y_pos += line_height
        
        self._render_text(panel_x + 15, y_pos, "Sent:", (0.8, 0.8, 0.8, 1.0))
        self._render_text(panel_x + 130, y_pos, str(node.packets_sent), (0.3, 0.7, 0.9, 1.0))
        y_pos += line_height
        
        self._render_text(panel_x + 15, y_pos, "Received:", (0.8, 0.8, 0.8, 1.0))
        self._render_text(panel_x + 130, y_pos, str(node.packets_received), (0.3, 0.9, 0.5, 1.0))
        y_pos += line_height
        
        self._render_text(panel_x + 15, y_pos, "Dropped:", (0.8, 0.8, 0.8, 1.0))
        self._render_text(panel_x + 130, y_pos, str(node.packets_dropped), (0.9, 0.3, 0.2, 1.0))
        y_pos += 30
        
        # Routing Table
        self._render_text(panel_x + 15, y_pos, "ROUTING TABLE:", (1.0, 1.0, 1.0, 1.0))
        y_pos += 20
        if not node.routing_table:
             self._render_text(panel_x + 15, y_pos, "(Empty)", (0.6, 0.6, 0.6, 1.0))
        else:
             sorted_rt = sorted(node.routing_table.items())
             for dest, hop in sorted_rt:
                 text = f"To {dest} -> Next: {hop}"
                 self._render_text(panel_x + 15, y_pos, text, (0.7, 0.9, 1.0, 1.0))
                 y_pos += 20

        # Restore matrices
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def handle_mouse_scroll(self, offset: float):
        """Handle mouse scroll for zoom in 2D"""
        zoom_factor = 1.1
        if offset > 0:
            self.zoom *= zoom_factor
        else:
            self.zoom /= zoom_factor
        
        # Clamp zoom
        self.zoom = max(10.0, min(200.0, self.zoom))
