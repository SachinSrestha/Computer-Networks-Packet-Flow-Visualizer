"""
Computer Networks Packet Flow Visualizer
Main entry point for the application
"""

import sys
import time
import json
import glfw
from OpenGL.GL import *
from OpenGL.GLUT import glutInit

from core.network import Network, Node, Link
from core.packet import Packet
from simulation.engine import SimulationEngine
from simulation.routing import DijkstraRouting
from graphics.renderer import Renderer
from graphics.ui import UI
import config


class PacketFlowVisualizer:
    """Main application class"""
    
    def __init__(self):
        """Initialize the visualizer"""
        self.window = None
        self.renderer = None
        self.ui = None
        self.network = Network("Demo Network")
        self.simulation = None
        
        # Topology management
        self.topologies = []
        self.current_topology_index = 0
        
        # Application state
        self.is_running = True
        self.last_frame_time = time.time()
        
        # Initialize components
        self._init_glfw()
        self._init_renderer()
        self._init_ui()
        self._load_demo_topology()
        self._init_simulation()
        
        print("="*60)
        print("Computer Networks Packet Flow Visualizer (2D)")
        print("="*60)
        print("\nControls:")
        print("  Mouse Click   : Select node (shows queue & congestion)")
        print("  Mouse Drag    : Drag Node (on node) or Pan Camera (on space)")
        print("  Mouse Wheel   : Zoom in/out")
        print("  C             : CONGEST selected node (Force traffic once)")
        print("  V             : TOGGLE CONSTANT CONGESTION (Keep full)")
        print("  P             : INJECT manual packet from selected node")
        print("  Space         : Pause/Resume simulation")
        print("  R             : Reset simulation")
        print("  1-9           : Set simulation speed (1x-9x)")
        print("  + / -         : Increase/Decrease speed")
        print("  N             : Generate new packet")
        print("  T             : Next topology")
        print("  ESC           : Exit")
        print("\nFeatures:")
        print("  • Store-and-forward packet switching with queues")
        print("  • Congestion detection (Green/Yellow/Red)")
        print("  • Adaptive routing (avoids congested nodes)")
        print("  • Real-time statistics panel")
        print("  • Interactive node selection")
        print("\n" + "="*60 + "\n")
    
    def _init_glfw(self):
        """Initialize GLFW and create window"""
        if not glfw.init():
            print("Failed to initialize GLFW")
            sys.exit(1)
            
        # Initialize GLUT for text rendering
        glutInit()
        
        # Set window hints - use compatibility profile for legacy OpenGL
        glfw.window_hint(glfw.SAMPLES, 4)  # 4x MSAA
        
        # Create window
        self.window = glfw.create_window(
            config.WINDOW_WIDTH,
            config.WINDOW_HEIGHT,
            config.WINDOW_TITLE,
            None,
            None
        )
        
        if not self.window:
            print("Failed to create GLFW window")
            glfw.terminate()
            sys.exit(1)
        
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)  # Enable vsync
        
        # Set callbacks
        glfw.set_framebuffer_size_callback(self.window, self._on_resize)
        glfw.set_key_callback(self.window, self._on_key)
        glfw.set_mouse_button_callback(self.window, self._on_mouse_button)
        glfw.set_cursor_pos_callback(self.window, self._on_mouse_move)
        glfw.set_scroll_callback(self.window, self._on_scroll)
    
    def _init_renderer(self):
        """Initialize the renderer"""
        self.renderer = Renderer(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
    
    def _init_ui(self):
        """Initialize the UI"""
        self.ui = UI(self.window)
    
    def _load_demo_topology(self):
        """Load a demo network topology"""
        try:
            with open('examples/demo_topologies.json', 'r') as f:
                data = json.load(f)
                self.topologies = data['topologies']
                self.current_topology_index = 0
                self._build_network_from_json(self.topologies[self.current_topology_index])
                print(f"Loaded topology: {self.topologies[self.current_topology_index]['name']}")
                print(f"Available topologies: {len(self.topologies)}")
        except Exception as e:
            print(f"Failed to load demo topology: {e}")
            print("Creating default topology...")
            self._create_default_topology()
    
    def _build_network_from_json(self, topology_data):
        """Build network from JSON data"""
        # Add nodes
        for node_data in topology_data['nodes']:
            node = Node(
                node_id=node_data['id'],
                position=tuple(node_data['position']),
                node_type=node_data.get('type', 'router'),
                name=node_data.get('name')
            )
            self.network.add_node(node)
        
        # Add links
        for link_data in topology_data['links']:
            link = Link(
                link_id=link_data['id'],
                source_id=link_data['source'],
                target_id=link_data['target'],
                bandwidth=link_data.get('bandwidth', 100),
                latency=link_data.get('latency', 10),
                bidirectional=link_data.get('bidirectional', True)
            )
            self.network.add_link(link)
    
    def _create_default_topology(self):
        """Create a simple default topology"""
        # Create nodes
        node_a = Node("A", (-3.0, 0.0, 0.0), "router", "Router A")
        node_b = Node("B", (0.0, 0.0, 0.0), "router", "Router B")
        node_c = Node("C", (3.0, 0.0, 0.0), "router", "Router C")
        
        self.network.add_node(node_a)
        self.network.add_node(node_b)
        self.network.add_node(node_c)
        
        # Create links
        link_ab = Link("AB", "A", "B", bandwidth=100, latency=10)
        link_bc = Link("BC", "B", "C", bandwidth=100, latency=10)
        
        self.network.add_link(link_ab)
        self.network.add_link(link_bc)
    
    def _init_simulation(self):
        """Initialize the simulation engine"""
        routing = DijkstraRouting(self.network)
        routing.update_routing_tables()
        self.simulation = SimulationEngine(self.network, routing)
        self.simulation.start()
    
    def switch_topology(self):
        """Switch to the next topology"""
        if not self.topologies:
            print("No topologies available")
            return
        
        # Move to next topology
        self.current_topology_index = (self.current_topology_index + 1) % len(self.topologies)
        
        # Clear current network
        self.network.clear()
        
        # Load new topology
        self._build_network_from_json(self.topologies[self.current_topology_index])
        
        # Reinitialize simulation
        routing = DijkstraRouting(self.network)
        routing.update_routing_tables()
        self.simulation = SimulationEngine(self.network, routing)
        self.simulation.start()
        
        print(f"\n{'='*60}")
        print(f"Switched to: {self.topologies[self.current_topology_index]['name']}")
        print(f"Description: {self.topologies[self.current_topology_index]['description']}")
        print(f"Topology {self.current_topology_index + 1} of {len(self.topologies)}")
        print(f"{'='*60}\n")
    
    def _on_resize(self, window, width, height):
        """Handle window resize"""
        self.renderer.resize(width, height)
    
    def _on_key(self, window, key, scancode, action, mods):
        """Handle keyboard input"""
        command = self.ui.handle_key_input(key, action)
        
        if command:
            self._handle_command(command)
    
    def _on_mouse_button(self, window, button, action, mods):
        """Handle mouse button events"""
        x, y = glfw.get_cursor_pos(window)
        
        # Check for node selection on left click
        if button == 0 and action == 1:  # Left click press
            selected_id = self.renderer.select_node_at(x, y, self.network)
            if selected_id:
                print(f"\n{'='*50}")
                print(f"Selected Node: {selected_id}")
                node = self.network.get_node(selected_id)
                if node:
                    print(f"  Queue: {node.queue.size()}/{node.queue.max_size}")
                    print(f"  Congestion: {node.congestion_state.upper()}")
                    print(f"  Packets Sent: {node.packets_sent}")
                    print(f"  Packets Received: {node.packets_received}")
                    print(f"  Packets Forwarded: {node.packets_forwarded}")
                    print(f"  Packets Dropped: {node.packets_dropped}")
                print(f"{'='*50}\n")
        
        self.renderer.handle_mouse_button(button, action, x, y, self.network)
    
    def _on_mouse_move(self, window, x, y):
        """Handle mouse movement"""
        self.renderer.handle_mouse_move(x, y, self.network)
    
    def _on_scroll(self, window, x_offset, y_offset):
        """Handle mouse scroll"""
        self.renderer.handle_mouse_scroll(y_offset)
    
    def _handle_command(self, command: str):
        """Handle UI commands"""
        if command == "toggle_pause":
            if self.simulation.is_running:
                self.simulation.pause()
                print("Simulation paused")
            else:
                self.simulation.start()
                print("Simulation resumed")
        
        elif command == "reset":
            self.simulation.reset()
            self.simulation.start()
            print("Simulation reset")
        
        elif command == "new_packet":
            self.simulation.generate_random_packet()
            print("Generated new packet")
        
        elif command == "toggle_topology":
            self.switch_topology()
        
        elif command == "exit":
            self.is_running = False
        
        elif command.startswith("set_speed:"):
            speed = float(command.split(":")[1])
            self.simulation.set_speed(speed)
            print(f"Simulation speed set to {speed}x")
        
        elif command == "speed_up":
            new_speed = min(self.simulation.simulation_speed + 0.5, config.MAX_SIMULATION_SPEED)
            self.simulation.set_speed(new_speed)
            print(f"Speed increased to {new_speed:.1f}x")
        
        elif command == "speed_down":
            new_speed = max(self.simulation.simulation_speed - 0.5, config.MIN_SIMULATION_SPEED)
            self.simulation.set_speed(new_speed)
            print(f"Speed decreased to {new_speed:.1f}x")
            
        elif command == "congest_node":
            selected_id = self.renderer.selected_node_id
            if selected_id:
                node = self.network.get_node(selected_id)
                if node:
                    print(f"Force congesting Node {selected_id}...")
                    # Fill queue with dummy packets
                    for i in range(25):
                        pkt = Packet(f"DUMMY_{i}", selected_id, "NOWHERE")
                        if not node.queue.enqueue(pkt):
                            break
                    node.update_congestion_state()
                    # Force routing update to reflect new cost immediately
                    self.simulation.routing_algorithm.update_routing_tables()
                    print(f"Node {selected_id} queue size: {node.queue.size()}/{node.queue.max_size}")
            else:
                print("No node selected! Click a node first.")
                
        elif command == "toggle_constant_congestion":
            selected_id = self.renderer.selected_node_id
            if selected_id:
                node = self.network.get_node(selected_id)
                if node:
                    node.force_congested = not node.force_congested
                    state = "ENABLED" if node.force_congested else "DISABLED"
                    print(f"Constant Congestion {state} for Node {selected_id}")
                    
                    if not node.force_congested:
                        node.queue.clear()
                        node.update_congestion_state()
                    
                    # Force routing update to reflect new cost immediately
                    self.simulation.routing_algorithm.update_routing_tables()
            else:
                print("No node selected! Click a node first.")

        elif command == "inject_packet":
            selected_id = self.renderer.selected_node_id
            if selected_id:
                # Find a random destination node that is not the source
                all_nodes = list(self.network.nodes.keys())
                if len(all_nodes) > 1:
                    import random
                    dest_opts = [nid for nid in all_nodes if nid != selected_id]
                    destination_id = random.choice(dest_opts)
                    
                    # Demonstration Mode: Clear and concise
                    # 1. Clear all existing active packets
                    self.simulation.active_packets.clear()
                    # 2. Clear all node queues to prevent collisions
                    for node in self.network.nodes.values():
                        # Don't clear if it's forced congested - we want that state to persist for the demo
                        if not getattr(node, "force_congested", False):
                            node.queue.clear()
                            node.update_congestion_state()
                    
                    # Force routing update BEFORE injection so the new packet uses the fresh "isolated" state
                    self.simulation.routing_algorithm.update_routing_tables()
                    
                    print("\n--- DEMONSTRATION MODE ---")
                    print("Clearing background traffic for clear demonstration...")
                    
                    # 3. Disable auto-generation
                    self.simulation.auto_generate = False
                    
                    # 4. Inject the packet and track it
                    # HEURISTIC: Intelligent destination choice for testing topologies
                    if "D" in all_nodes and (selected_id == "A" or selected_id == "S"):
                        destination_id = "D"
                    elif selected_id == "A" and "C" in all_nodes:
                        destination_id = "C"
                    elif selected_id.startswith("L") and any(n.startswith("R") for n in all_nodes):
                        # Bottleneck Bridge: Left nodes send to a Right node
                        right_nodes = [n for n in all_nodes if n.startswith("R")]
                        destination_id = random.choice(right_nodes)
                    else:
                        destination_id = random.choice(dest_opts)
                        
                    pkt = self.simulation.generate_packet(selected_id, destination_id)
                    if pkt:
                        self.simulation.demo_packet_id = pkt.id
                        print(f"Injecting Demonstration Packet: {selected_id} -> {destination_id}")
                    else:
                        print("Failed to generate packet.")
                        self.simulation.auto_generate = True # Restore if failed
                else:
                    print("Error: Need at least 2 nodes to inject a packet.")
            else:
                print("No node selected! Select a source node first.")
    
    def run(self):
        """Main application loop"""
        while self.is_running and not glfw.window_should_close(self.window):
            # Calculate delta time
            current_time = time.time()
            delta_time = current_time - self.last_frame_time
            self.last_frame_time = current_time
            
            # Update simulation
            self.simulation.update(delta_time)
            
            # Update UI
            self.ui.update(delta_time)
            
            # Get current statistics
            stats = self.simulation.get_statistics()
            
            # Render with statistics
            self.renderer.render(self.network, self.simulation.active_packets, stats)
            
            # Swap buffers and poll events
            glfw.swap_buffers(self.window)
            glfw.poll_events()
            
            # Print statistics periodically (every 5 seconds)
            if int(current_time) % 5 == 0 and delta_time < 0.1:
                stats = self.simulation.get_statistics()
                if stats['total_generated'] > 0:  # Only print if there are packets
                    self.ui.print_console_stats(stats)
        
        self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        print("\nShutting down...")
        
        # Print final statistics
        stats = self.simulation.get_statistics()
        print("\nFinal Statistics:")
        self.ui.print_console_stats(stats)
        
        glfw.terminate()


def main():
    """Main entry point"""
    try:
        app = PacketFlowVisualizer()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
