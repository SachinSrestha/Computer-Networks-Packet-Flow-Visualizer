"""
Utilities package for animations and helper functions
"""

from .animation import interpolate, bezier_curve, ease_in_out
from .helpers import distance_3d, normalize_vector, random_color, hex_to_rgb

__all__ = ['interpolate', 'bezier_curve', 'ease_in_out', 
           'distance_3d', 'normalize_vector', 'random_color', 'hex_to_rgb']
