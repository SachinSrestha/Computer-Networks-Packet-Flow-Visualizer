"""
UI controls and display for the network visualizer
"""

import glfw
from typing import Dict, Optional
import config


class UI:
    """User interface manager for controls and information display"""
    
    def __init__(self, window):
        """
        Initialize the UI
        
        Args:
            window: GLFW window handle
        """
        self.window = window
        self.show_help = True
        self.show_stats = True
        
        # UI state
        self.selected_node_id = None
        self.message = ""
        self.message_time = 0.0
        self.status_message = "" # Persistent status like "Link Mode: Select Target"
    
    def render_text_overlay(self, simulation_stats):
        """Render text overlay (placeholder)"""
        pass
    
    def show_message(self, message, duration=3.0):
        """Show a temporary message"""
        self.message = message
        self.message_time = duration
    
    def update(self, delta_time):
        """Update UI state"""
        if self.message_time > 0:
            self.message_time -= delta_time
            if self.message_time <= 0:
                self.message = ""
    
    def toggle_help(self):
        """Toggle help display"""
        self.show_help = not self.show_help
    
    def toggle_stats(self):
        """Toggle statistics display"""
        self.show_stats = not self.show_stats
    
    def get_help_text(self):
        """Get help text for controls"""
        status = ""
        if self.status_message:
            status = "\n        STATUS: " + self.status_message + "\n        " + "-"*29 + "\n"
            
        return """
        CONTROLS:
        -----------------------------""" + status + """
        Mouse Drag    : Pan camera (on space) or Drag Node
        Mouse Click   : Select node
        Mouse Wheel   : Zoom in/out
        Space         : Pause/Resume
        A             : Add Node at mouse position
        L             : Create Link (Select source first, then press L, then click target)
        DEL           : Delete Selected Node
        X             : Clear Entire Topology
        R             : Reset simulation
        1-9           : Change speed
        N             : New packet
        H             : Toggle help
        S             : Toggle stats
        ESC           : Exit
        -----------------------------
        MANUAL TRAFFIC (Selected Node):
        P             : Inject Single Packet
        C             : Congest Once (Fill Queue)
        V             : Toggle Constant Congestion
        """
    
    def get_stats_text(self, stats):
        """Get formatted statistics text"""
        total = stats.get('total_generated', 0)
        active = stats.get('active', 0)
        delivered = stats.get('delivered', 0)
        dropped = stats.get('dropped', 0)
        rate = round(stats.get('delivery_rate', 0), 1)
        latency = round(stats.get('average_latency', 0), 2)
        sim_time = round(stats.get('simulation_time', 0), 1)
        
        return """
        STATISTICS:
        -----------------------------
        Total Generated : {}
        Active Packets  : {}
        Delivered       : {}
        Dropped         : {}
        Delivery Rate   : {} %
        Avg Latency     : {} ms
        Sim Time        : {} s
        """.format(total, active, delivered, dropped, rate, latency, sim_time)
    
    def handle_key_input(self, key, action):
        """Handle keyboard input"""
        if action != glfw.PRESS:
            return None
        
        # Map keys to commands
        if key == glfw.KEY_SPACE:
            return "toggle_pause"
        elif key == glfw.KEY_R:
            return "reset"
        elif key == glfw.KEY_N:
            return "new_packet"
        elif key == glfw.KEY_H:
            self.toggle_help()
            return None
        elif key == glfw.KEY_S:
            self.toggle_stats()
            return None
        elif key == glfw.KEY_T:
            return "toggle_topology"
        elif key == glfw.KEY_C:
            return "congest_node"
        elif key == glfw.KEY_V:
            return "toggle_constant_congestion"
        elif key == glfw.KEY_P:
            return "inject_packet"
        elif key == glfw.KEY_ESCAPE:
            return "exit"
        elif glfw.KEY_1 <= key <= glfw.KEY_9:
            speed = key - glfw.KEY_0
            return "set_speed:" + str(speed)
        elif key == glfw.KEY_A:
            return "add_node"
        elif key == glfw.KEY_L:
            return "start_link"
        elif key == glfw.KEY_DELETE:
            return "remove_node"
        elif key == glfw.KEY_X:
            return "clear_topology"
        elif key == glfw.KEY_EQUAL or key == glfw.KEY_KP_ADD:
            return "speed_up"
        elif key == glfw.KEY_MINUS or key == glfw.KEY_KP_SUBTRACT:
            return "speed_down"
        
        return None
    
    def print_console_stats(self, stats):
        """Print statistics to console"""
        rate = round(stats.get('delivery_rate', 0), 2)
        latency = round(stats.get('average_latency', 0), 2)
        sim_time = round(stats.get('simulation_time', 0), 2)
        
        print("\n" + "="*50)
        print("NETWORK PACKET FLOW VISUALIZER - STATISTICS")
        print("="*50)
        print("Total Packets Generated : " + str(stats.get('total_generated', 0)))
        print("Active Packets          : " + str(stats.get('active', 0)))
        print("Delivered Packets       : " + str(stats.get('delivered', 0)))
        print("Dropped Packets         : " + str(stats.get('dropped', 0)))
        print("Delivery Rate           : " + str(rate) + "%")
        print("Average Latency         : " + str(latency) + " ms")
        print("Simulation Time         : " + str(sim_time) + " s")
        print("="*50 + "\n")
