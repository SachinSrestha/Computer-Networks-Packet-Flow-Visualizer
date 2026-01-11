"""
Animation utilities for smooth interpolation and curves
"""

import numpy as np
from typing import List, Tuple
import config


def interpolate(start: float, end: float, t: float) -> float:
    """
    Linear interpolation between two values
    
    Args:
        start: Start value
        end: End value
        t: Interpolation factor (0.0 to 1.0)
        
    Returns:
        Interpolated value
    """
    return start + (end - start) * t


def interpolate_vector(start: np.ndarray, end: np.ndarray, t: float) -> np.ndarray:
    """
    Linear interpolation between two vectors
    
    Args:
        start: Start vector
        end: End vector
        t: Interpolation factor (0.0 to 1.0)
        
    Returns:
        Interpolated vector
    """
    return start + (end - start) * t


def ease_in_out(t: float) -> float:
    """
    Ease-in-out interpolation function
    
    Args:
        t: Input value (0.0 to 1.0)
        
    Returns:
        Eased value (0.0 to 1.0)
    """
    if t < 0.5:
        return 2 * t * t
    else:
        return 1 - 2 * (1 - t) * (1 - t)


def ease_in(t: float) -> float:
    """
    Ease-in interpolation function
    
    Args:
        t: Input value (0.0 to 1.0)
        
    Returns:
        Eased value (0.0 to 1.0)
    """
    return t * t


def ease_out(t: float) -> float:
    """
    Ease-out interpolation function
    
    Args:
        t: Input value (0.0 to 1.0)
        
    Returns:
        Eased value (0.0 to 1.0)
    """
    return 1 - (1 - t) * (1 - t)


def bezier_curve(p0: np.ndarray, p1: np.ndarray, p2: np.ndarray, 
                 p3: np.ndarray, t: float) -> np.ndarray:
    """
    Cubic Bezier curve interpolation
    
    Args:
        p0: Start point
        p1: First control point
        p2: Second control point
        p3: End point
        t: Interpolation factor (0.0 to 1.0)
        
    Returns:
        Point on the Bezier curve
    """
    u = 1 - t
    tt = t * t
    uu = u * u
    uuu = uu * u
    ttt = tt * t
    
    point = uuu * p0  # (1-t)^3 * P0
    point += 3 * uu * t * p1  # 3(1-t)^2 * t * P1
    point += 3 * u * tt * p2  # 3(1-t) * t^2 * P2
    point += ttt * p3  # t^3 * P3
    
    return point


def generate_bezier_path(start: np.ndarray, end: np.ndarray, 
                         segments: int = None) -> List[np.ndarray]:
    """
    Generate a smooth Bezier curve path between two points
    
    Args:
        start: Start position
        end: End position
        segments: Number of segments (default from config)
        
    Returns:
        List of points along the curve
    """
    if segments is None:
        segments = config.BEZIER_CURVE_SEGMENTS
    
    # Calculate control points for a smooth arc
    direction = end - start
    distance = np.linalg.norm(direction)
    
    # Create control points offset perpendicular to the line
    midpoint = (start + end) / 2
    perpendicular = np.array([-direction[2], 0, direction[0]])
    
    if np.linalg.norm(perpendicular) > 0:
        perpendicular = perpendicular / np.linalg.norm(perpendicular)
    else:
        perpendicular = np.array([0, 1, 0])
    
    offset = distance * 0.2
    p1 = start + perpendicular * offset
    p2 = end + perpendicular * offset
    
    # Generate points along the curve
    points = []
    for i in range(segments + 1):
        t = i / segments
        point = bezier_curve(start, p1, p2, end, t)
        points.append(point)
    
    return points


def smooth_step(edge0: float, edge1: float, x: float) -> float:
    """
    Smooth step function (Hermite interpolation)
    
    Args:
        edge0: Lower edge
        edge1: Upper edge
        x: Input value
        
    Returns:
        Smoothly interpolated value
    """
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def lerp_angle(start: float, end: float, t: float) -> float:
    """
    Linear interpolation for angles (handles wrapping)
    
    Args:
        start: Start angle in degrees
        end: End angle in degrees
        t: Interpolation factor (0.0 to 1.0)
        
    Returns:
        Interpolated angle in degrees
    """
    # Normalize angles to [0, 360)
    start = start % 360
    end = end % 360
    
    # Find shortest path
    diff = end - start
    if diff > 180:
        diff -= 360
    elif diff < -180:
        diff += 360
    
    return start + diff * t
