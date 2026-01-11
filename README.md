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

### 4. **Modern UI & Interaction**
- **Draggable Nodes**: Rearrange the network layout in real-time by clicking and dragging nodes.
- **Live Statistics**: Monitor Delivery Rate, Latency, and Throughput in an overlay panel.
- **Routing Table Inspector**: Select any node to view its real-time routing table and specific costs.
- **Rich Aesthetics**: Vibrant colors, smooth triangle-arrow packets, and high-precision labels.

---

## 🎮 Controls & Interaction

| Key | Action |
|-----|--------|
| **Mouse Left Click** | Select a node to inspect stats & routing table |
| **Mouse Left Drag (Node)** | Rearrange nodes in the topology |
| **Mouse Left Drag (BG)** | Pan the camera |
| **Mouse Wheel** | Zoom in/out |
| **`T`** | Switch between topologies (Diamond, Highway, Ring, etc.) |
| **`P`** | **Smart Inject**: Clear traffic and send a demonstration packet |
| **`V`** | **Lock Congestion**: Force a selected node into a permanent high-cost state |
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
- **Routing Engine**: Custom Dijkstra implementation using priority heaps
- **Data Model**: JSON-based topology definitions in `examples/demo_topologies.json`
- **Animation Engine**: Linear interpolation (`lerp`) for smooth packet traversal

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.8+
- Dependencies: `pip install PyOpenGL glfw numpy`

### 2. Run
```bash
python main.py
```

### 3. Proposed Test Scenario
1. Switch to **Diamond Rerouting Test** (`T` key).
2. Note that the default path is A -> B -> D.
3. Select **Node B** and press **`V`** to congest it.
4. Press **`P`** on **Node A**.
5. Observe the demonstration packet immediately rerouting via **Node C** due to the massive cost penalty on B.

---

## 📚 Network Topologies Included
- **Diamond Rerouting**: The classic adaptive routing test.
- **Redundant Triangle**: Demonstrates bypassing slow direct links for multi-hop paths.
- **Dual Highway**: Contrasts hop-count (Upper) vs. Latency (Lower).
- **Bottleneck Bridge**: Illustrates single-point-of-failure and choke points.
- **Star & Ring**: Standard distributed network layouts.

---

**Status**: ✅ **Production-Ready Visualizer**
Created for COMP 342 - Advanced Computer Graphics & Networking Integration.
