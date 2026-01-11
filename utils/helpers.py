"""
Helper utilities for math operations and color handling
"""

import numpy as np
import random
from typing import Tuple


def distance_3d(p1: np.ndarray, p2: np.ndarray) -> float:
    """
    Calculate Euclidean distance between two 3D points
    
    Args:
        p1: First point
        p2: Second point
        
    Returns:
        Distance between points
    """
    return np.linalg.norm(p2 - p1)


def normalize_vector(v: np.ndarray) -> np.ndarray:
    """
    Normalize a vector to unit length
    
    Args:
        v: Input vector
        
    Returns:
        Normalized vector
    """
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def cross_product(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    """
    Calculate cross product of two 3D vectors
    
    Args:
        v1: First vector
        v2: Second vector
        
    Returns:
        Cross product vector
    """
    return np.cross(v1, v2)


def dot_product(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Calculate dot product of two vectors
    
    Args:
        v1: First vector
        v2: Second vector
        
    Returns:
        Dot product
    """
    return np.dot(v1, v2)


def random_color(alpha: float = 1.0) -> np.ndarray:
    """
    Generate a random color
    
    Args:
        alpha: Alpha channel value (0.0 to 1.0)
        
    Returns:
        RGBA color array
    """
    return np.array([
        random.random(),
        random.random(),
        random.random(),
        alpha
    ], dtype=np.float32)


def hex_to_rgb(hex_color: str) -> Tuple[float, float, float]:
    """
    Convert hex color string to RGB tuple
    
    Args:
        hex_color: Hex color string (e.g., "#FF5733" or "FF5733")
        
    Returns:
        RGB tuple with values from 0.0 to 1.0
    """
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return (r, g, b)


def rgb_to_hex(r: float, g: float, b: float) -> str:
    """
    Convert RGB values to hex color string
    
    Args:
        r: Red component (0.0 to 1.0)
        g: Green component (0.0 to 1.0)
        b: Blue component (0.0 to 1.0)
        
    Returns:
        Hex color string
    """
    r_int = int(r * 255)
    g_int = int(g * 255)
    b_int = int(b * 255)
    return f"#{r_int:02X}{g_int:02X}{b_int:02X}"


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp a value between min and max
    
    Args:
        value: Input value
        min_value: Minimum value
        max_value: Maximum value
        
    Returns:
        Clamped value
    """
    return max(min_value, min(max_value, value))


def map_range(value: float, in_min: float, in_max: float, 
              out_min: float, out_max: float) -> float:
    """
    Map a value from one range to another
    
    Args:
        value: Input value
        in_min: Input range minimum
        in_max: Input range maximum
        out_min: Output range minimum
        out_max: Output range maximum
        
    Returns:
        Mapped value
    """
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def random_position_in_sphere(radius: float) -> np.ndarray:
    """
    Generate a random position within a sphere
    
    Args:
        radius: Sphere radius
        
    Returns:
        Random 3D position
    """
    # Use rejection sampling for uniform distribution
    while True:
        x = random.uniform(-radius, radius)
        y = random.uniform(-radius, radius)
        z = random.uniform(-radius, radius)
        
        if x*x + y*y + z*z <= radius*radius:
            return np.array([x, y, z], dtype=np.float32)


def random_position_on_sphere(radius: float) -> np.ndarray:
    """
    Generate a random position on the surface of a sphere
    
    Args:
        radius: Sphere radius
        
    Returns:
        Random 3D position on sphere surface
    """
    theta = random.uniform(0, 2 * np.pi)
    phi = random.uniform(0, np.pi)
    
    x = radius * np.sin(phi) * np.cos(theta)
    y = radius * np.sin(phi) * np.sin(theta)
    z = radius * np.cos(phi)
    
    return np.array([x, y, z], dtype=np.float32)
