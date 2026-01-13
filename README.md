# Computer Networks Packet Flow Visualizer (2D)

A high-fidelity 2D visualization tool designed to demonstrate core computer networking principles. Built with **Python** and **OpenGL**, it provides an interactive laboratory for observing packet flow, congestion control, and adaptive routing algorithms in real-time.

---

## 🎯 Project Objectives
This project integrates **Computer Graphics** (rendering, animation, UI design) and **Computer Networks** (queuing theory, pathfinding, traffic management) to create a comprehensive educational tool.

---

## ✨ Advanced Features

### 1. **Adaptive Dijkstra Routing**
- **Dynamic Link Costing**: Link costs are not static! They scale **linearly** with node congestion.
- **Granular Costs**: Real-time decimal costs (e.g., `Cost: 14.5`) reflect the exact state of node queues.
- **Rerouting**: The simulation uses Dijkstra's algorithm to calculate the most efficient path. Packets will automatically bypass high-cost/congested nodes.

### 2. **Store-and-Forward Logic**
- **Buffer Management**: Every router (node) has a FIFO queue.
- **Bottleneck Analysis**: Nodes change color (**Green** → **Yellow** → **Red**) based on queue occupancy.
- **Packet Loss**: Visual indicators (White 'X') show when a packet is dropped due to full buffers.

### 3. **Smart Injection & Demonstration Mode**
- **Isolated Testing**: Press **`P`** on a selected node to clear all background traffic and queues.
- **Deterministic Paths**: A single "Demonstration Packet" is injected, allowing you to track its journey across a clean network.
- **Topology Awareness**: Injection targets are automatically optimized for the current topology (e.g., A -> D in Diamond).

### 4. **Dynamic Topology Builder (Sandbox)**
- **Real-time Construction**: Build your own network from scratch within the application.
- **Node & Link Tools**: Add nodes at mouse positions and connect them with distance-aware links.
- **Auto-Routing Updates**: The system automatically clears and recomputes all routing tables whenever the topology changes (add/remove node or link).
- **Interactive Repositioning**: Drag nodes to new locations; link costs (latencies) will recalculate live based on the new physical distance.

### 5. **Modern UI & Interaction**
- **Overlay Statistics**: Monitor global performance (Delivery Rate, Latency) and per-node queue bars.
- **Routing Table Inspector**: Select any node to view its real-time routing table and the dynamic costs of its neighbors.
- **Rich Aesthetics**: Vibrant, high-contrast colors, smooth triangle-arrow packets, and pixel-perfect labels.

---

## 🎮 Controls & Interaction

| Key | Action |
|-----|--------|
| **Mouse Left Click** | Select a node to inspect stats & routing table |
| **Mouse Left Drag (Node)** | Rearrange nodes (Live cost/routing update) |
| **Mouse Left Drag (BG)** | Pan the camera (on space) |
| **Mouse Wheel** | Zoom in/out |
| **`A`** | **Add Node**: Create a new router at the mouse position |
| **`L`** | **Create Link**: Click source node -> Press L -> Click target node |
| **`DEL`** | **Delete Node**: Remove selected node and its links |
| **`X`** | **Clear All**: Wipe the entire workspace to start fresh |
| **`T`** | Switch between topologies (Diamond, Highway, **Blank Sandbox**, etc.) |
| **`P`** | **Smart Inject**: Clear traffic and send a demonstration packet |
| **`V`** | **Lock Congestion**: Force fixed high congestion on a node |
| **`C`** | **Impulse Congestion**: Briefly flood a node with dummy packets |
| **`N`** | Manually generate a single random background packet |
| **`Space`** | Pause/Resume the simulation |
| **`R`** | Full reset of the current simulation |
| **`1-9`** | Set simulation speed (Time Scaling) |
| **`ESC`** | Exit Application |

---

## 🏗️ Technical Architecture

- **Graphics Backend**: OpenGL via PyOpenGL
- **Input Management**: GLFW for high-performance keyboard/mouse event handling
- **Routing Engine**: Custom Dijkstra implementation with **Dynamic Metric Recalculation**
- **Data Model**: JSON-based presets and live memory-mapped structure for custom edits
- **Distance Logic**: Euclidean distance-to-latency mapping ($Cost \propto \sqrt{\Delta x^2 + \Delta z^2}$)

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.8+
- Dependencies: `pip install PyOpenGL glfw numpy`
- *Note: Ensure your environment supports standard ASCII and modern Python f-strings.*

### 2. Run
```bash
python main.py
```

### 3. Proposed Sandbox Scenario
1. Switch to **Blank Sandbox** (`T` key) or press **`X`**.
2. Press **`A`** in three different spots to create nodes **N1, N2, N3**.
3. Create a triangle: Link N1->N2, N2->N3, and N1->N3 using the **`L`** key workflow.
4. Drag **N2** very far away and watch the **Cost** label on its links increase.
5. Inject a packet from **N1** to **N3** (`P` key) and see it choose the direct path or the detour via N2 depending on your placement!

---

## 📚 Network Topologies Included
- **Diamond Rerouting**: The classic adaptive routing test.
- **Redundant Triangle**: Demonstrates bypassing slow direct links.
- **Dual Highway**: Contrasts hop-count vs. physical Latency.
- **Bottleneck Bridge**: Illustrates choke points.
- **Blank Sandbox**: A perfectly clean state for custom construction.

---

**Status**: ✅ **Interactive Networking Laboratory (v2.0)**
Created for COMP 342 - Advanced Computer Graphics & Networking Integration.
