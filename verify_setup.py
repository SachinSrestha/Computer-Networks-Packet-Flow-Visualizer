#!/usr/bin/env python3
"""
Quick Start Guide and Test Script
Run this to verify your installation
"""

import sys

def check_imports():
    """Check if all required libraries are installed"""
    print("="*60)
    print("Checking Required Libraries...")
    print("="*60)
    
    required_modules = {
        'OpenGL': 'PyOpenGL',
        'glfw': 'glfw',
        'numpy': 'numpy',
        'pyrr': 'pyrr',
        'PIL': 'Pillow'
    }
    
    all_ok = True
    for module, package in required_modules.items():
        try:
            __import__(module)
            print(f"✅ {package:20s} - OK")
        except ImportError:
            print(f"❌ {package:20s} - MISSING")
            all_ok = False
    
    print("="*60)
    return all_ok

def check_project_structure():
    """Check if all project files exist"""
    print("\nChecking Project Structure...")
    print("="*60)
    
    import os
    
    required_files = [
        'main.py',
        'config.py',
        'requirements.txt',
        'README.md',
        'core/__init__.py',
        'core/network.py',
        'core/packet.py',
        'simulation/__init__.py',
        'simulation/engine.py',
        'simulation/routing.py',
        'graphics/__init__.py',
        'graphics/renderer.py',
        'graphics/ui.py',
        'utils/__init__.py',
        'utils/animation.py',
        'utils/helpers.py',
        'examples/demo_topologies.json'
    ]
    
    all_ok = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file:40s} - Found")
        else:
            print(f"❌ {file:40s} - Missing")
            all_ok = False
    
    print("="*60)
    return all_ok

def test_imports():
    """Test importing project modules"""
    print("\nTesting Project Imports...")
    print("="*60)
    
    try:
        from core.network import Network, Node, Link
        print("✅ core.network - OK")
    except Exception as e:
        print(f"❌ core.network - ERROR: {e}")
        return False
    
    try:
        from core.packet import Packet, PacketQueue
        print("✅ core.packet - OK")
    except Exception as e:
        print(f"❌ core.packet - ERROR: {e}")
        return False
    
    try:
        from simulation.engine import SimulationEngine
        print("✅ simulation.engine - OK")
    except Exception as e:
        print(f"❌ simulation.engine - ERROR: {e}")
        return False
    
    try:
        from simulation.routing import DijkstraRouting, FloodingRouting
        print("✅ simulation.routing - OK")
    except Exception as e:
        print(f"❌ simulation.routing - ERROR: {e}")
        return False
    
    try:
        from graphics.renderer import Renderer
        print("✅ graphics.renderer - OK")
    except Exception as e:
        print(f"❌ graphics.renderer - ERROR: {e}")
        return False
    
    try:
        from graphics.ui import UI
        print("✅ graphics.ui - OK")
    except Exception as e:
        print(f"❌ graphics.ui - ERROR: {e}")
        return False
    
    try:
        from utils.animation import interpolate, bezier_curve
        print("✅ utils.animation - OK")
    except Exception as e:
        print(f"❌ utils.animation - ERROR: {e}")
        return False
    
    try:
        from utils.helpers import distance_3d, random_color
        print("✅ utils.helpers - OK")
    except Exception as e:
        print(f"❌ utils.helpers - ERROR: {e}")
        return False
    
    print("="*60)
    return True

def main():
    """Main test function"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  Computer Networks Packet Flow Visualizer".center(58) + "║")
    print("║" + "  Installation Verification".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    print("\n")
    
    # Check libraries
    libs_ok = check_imports()
    
    # Check project structure
    structure_ok = check_project_structure()
    
    # Test imports
    imports_ok = test_imports()
    
    # Final result
    print("\n")
    print("="*60)
    print("VERIFICATION RESULTS")
    print("="*60)
    
    if libs_ok and structure_ok and imports_ok:
        print("✅ ALL CHECKS PASSED!")
        print("\n🚀 Your project is ready to run!")
        print("\nTo start the visualizer, run:")
        print("    python main.py")
        print("\n")
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print("\nPlease fix the issues above before running the visualizer.")
        if not libs_ok:
            print("\n📦 To install missing libraries:")
            print("    pip install -r requirements.txt")
        print("\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
