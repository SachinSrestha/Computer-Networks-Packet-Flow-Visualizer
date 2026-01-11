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
        self.selected_node_id: Optional[str] = None
        self.message = ""
        self.message_time = 0.0
    
    def render_text_overlay(self, simulation_stats: Dict):
        """
        Render text overlay with statistics and controls
        
        Args:
            simulation_stats: Dictionary of simulation statistics
        """
        # Note: This is a placeholder for text rendering
        # In a full implementation, you would use a library like imgui or render text to texture
        pass
    
    def show_message(self, message: str, duration: float = 3.0):
        """
        Show a temporary message
        
        Args:
            message: Message to display
            duration: Duration in seconds
        """
        self.message = message
        self.message_time = duration
    
    def update(self, delta_time: float):
        """
        Update UI state
        
        Args:
            delta_time: Time elapsed since last update
        """
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
    
    def get_help_text(self) -> str:
        """Get help text for controls"""
        return """
        CONTROLS:
        ─────────────────────────────
        Mouse Drag    : Rotate camera
        Mouse Wheel   : Zoom in/out
        Space         : Pause/Resume
        R             : Reset simulation
        1-9           : Change speed
        N             : New packet
        H             : Toggle help
        S             : Toggle stats
        ESC           : Exit
        """
    
    def get_stats_text(self, stats: Dict) -> str:
        """
        Get formatted statistics text
        
        Args:
            stats: Statistics dictionary
            
        Returns:
            Formatted statistics string
        """
        return f"""
        STATISTICS:
        ─────────────────────────────
        Total Generated : {stats.get('total_generated', 0)}
        Active Packets  : {stats.get('active', 0)}
        Delivered       : {stats.get('delivered', 0)}
        Dropped         : {stats.get('dropped', 0)}
        Delivery Rate   : {stats.get('delivery_rate', 0):.1f}%
        Avg Latency     : {stats.get('average_latency', 0):.2f} ms
        Sim Time        : {stats.get('simulation_time', 0):.1f} s
        """
    
    def handle_key_input(self, key: int, action: int) -> Optional[str]:
        """
        Handle keyboard input
        
        Args:
            key: GLFW key code
            action: GLFW action (press, release, repeat)
            
        Returns:
            Command string or None
        """
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
            return f"set_speed:{speed}"
        elif key == glfw.KEY_EQUAL or key == glfw.KEY_KP_ADD:  # + key
            return "speed_up"
        elif key == glfw.KEY_MINUS or key == glfw.KEY_KP_SUBTRACT:  # - key
            return "speed_down"
        
        return None
    
    def print_console_stats(self, stats: Dict):
        """
        Print statistics to console
        
        Args:
            stats: Statistics dictionary
        """
        print("\n" + "="*50)
        print("NETWORK PACKET FLOW VISUALIZER - STATISTICS")
        print("="*50)
        print(f"Total Packets Generated : {stats.get('total_generated', 0)}")
        print(f"Active Packets          : {stats.get('active', 0)}")
        print(f"Delivered Packets       : {stats.get('delivered', 0)}")
        print(f"Dropped Packets         : {stats.get('dropped', 0)}")
        print(f"Delivery Rate           : {stats.get('delivery_rate', 0):.2f}%")
        print(f"Average Latency         : {stats.get('average_latency', 0):.2f} ms")
        print(f"Simulation Time         : {stats.get('simulation_time', 0):.2f} s")
        print("="*50 + "\n")
