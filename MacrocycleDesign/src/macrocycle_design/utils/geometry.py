"""Geometry utilities for macrocycle_design.

This module provides functions for geometric calculations commonly used in
macromolecular modeling, such as distance, angle, and dihedral calculations,
as well as coordinate transformations and vector operations.
"""

import numpy as np
from typing import Tuple, List, Union, Optional
import math

# Type aliases
Vector3D = np.ndarray  # Shape: (3,)
Matrix3D = np.ndarray  # Shape: (3, 3)
Points3D = np.ndarray  # Shape: (n, 3)

def distance(p1: Vector3D, p2: Vector3D) -> float:
    """Calculate the Euclidean distance between two points in 3D space.
    
    Args:
        p1: First point (x, y, z)
        p2: Second point (x, y, z)
        
    Returns:
        float: Distance between p1 and p2
    """
    return np.linalg.norm(p2 - p1)

def angle(p1: Vector3D, p2: Vector3D, p3: Vector3D, degrees: bool = True) -> float:
    """Calculate the angle between three points (p1-p2-p3).
    
    Args:
        p1: First point
        p2: Middle point (vertex)
        p3: Third point
        degrees: If True, return angle in degrees; otherwise in radians
        
    Returns:
        float: Angle in degrees or radians
    """
    v1 = p1 - p2
    v2 = p3 - p2
    
    cos_theta = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    # Handle floating point errors
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    
    theta = np.arccos(cos_theta)
    
    return np.degrees(theta) if degrees else theta

def dihedral(p1: Vector3D, p2: Vector3D, p3: Vector3D, p4: Vector3D, 
            degrees: bool = True) -> float:
    """Calculate the dihedral angle between four points (p1-p2-p3-p4).
    
    Args:
        p1: First point
        p2: Second point
        p3: Third point
        p4: Fourth point
        degrees: If True, return angle in degrees; otherwise in radians
        
    Returns:
        float: Dihedral angle in degrees or radians
    """
    # Calculate vectors
    b1 = p2 - p1
    b2 = p3 - p2
    b3 = p4 - p3
    
    # Calculate normals to the planes
    n1 = np.cross(b1, b2)
    n2 = np.cross(b2, b3)
    
    # Calculate the angle between the normals
    cos_phi = np.dot(n1, n2) / (np.linalg.norm(n1) * np.linalg.norm(n2))
    # Handle floating point errors
    cos_phi = np.clip(cos_phi, -1.0, 1.0)
    
    # Calculate the sign of the dihedral angle
    sign = np.sign(np.dot(np.cross(n1, n2), b2))
    phi = sign * np.arccos(cos_phi)
    
    # Convert to degrees if requested
    if degrees:
        phi = np.degrees(phi)
    
    return phi

def center_of_mass(coords: Points3D, masses: Optional[np.ndarray] = None) -> Vector3D:
    """Calculate the center of mass of a set of points.
    
    Args:
        coords: Array of coordinates (n_atoms, 3)
        masses: Optional array of masses (n_atoms,). If None, assumes uniform masses.
        
    Returns:
        Vector3D: Center of mass coordinates (3,)
    """
    if masses is None:
        return np.mean(coords, axis=0)
    else:
        return np.sum(coords * masses[:, np.newaxis], axis=0) / np.sum(masses)

def rmsd(coords1: Points3D, coords2: Points3D) -> float:
    """Calculate the root-mean-square deviation (RMSD) between two sets of coordinates.
    
    Args:
        coords1: First set of coordinates (n_atoms, 3)
        coords2: Second set of coordinates (n_atoms, 3)
        
    Returns:
        float: RMSD in the same units as the input coordinates
    """
    if coords1.shape != coords2.shape:
        raise ValueError("Coordinate arrays must have the same shape")
    
    diff = coords1 - coords2
    return np.sqrt(np.mean(np.sum(diff**2, axis=1)))

def kabsch_rotation_matrix(coords1: Points3D, coords2: Points3D) -> Matrix3D:
    """Calculate the optimal rotation matrix to align coords1 to coords2 using the Kabsch algorithm.
    
    Args:
        coords1: Reference coordinates (n_atoms, 3)
        coords2: Target coordinates (n_atoms, 3)
        
    Returns:
        Matrix3D: 3x3 rotation matrix
    """
    if coords1.shape != coords2.shape:
        raise ValueError("Coordinate arrays must have the same shape")
    
    # Center the coordinates
    center1 = np.mean(coords1, axis=0)
    center2 = np.mean(coords2, axis=0)
    
    coords1_centered = coords1 - center1
    coords2_centered = coords2 - center2
    
    # Calculate the covariance matrix
    cov = coords2_centered.T @ coords1_centered
    
    # Singular value decomposition
    U, S, Vt = np.linalg.svd(cov)
    
    # Ensure a right-handed coordinate system
    d = np.sign(np.linalg.det(U @ Vt))
    I = np.eye(3)
    I[2, 2] = d
    
    # Calculate the rotation matrix
    R = U @ I @ Vt
    
    return R

def align_structures(coords1: Points3D, coords2: Points3D) -> Tuple[Points3D, float]:
    """Align coords1 to coords2 using the Kabsch algorithm.
    
    Args:
        coords1: Reference coordinates (n_atoms, 3)
        coords2: Target coordinates (n_atoms, 3)
        
    Returns:
        Tuple containing:
            - Aligned coordinates of coords1
            - RMSD after alignment
    """
    if coords1.shape != coords2.shape:
        raise ValueError("Coordinate arrays must have the same shape")
    
    # Center the coordinates
    center1 = np.mean(coords1, axis=0)
    center2 = np.mean(coords2, axis=0)
    
    coords1_centered = coords1 - center1
    coords2_centered = coords2 - center2
    
    # Calculate the rotation matrix
    R = kabsch_rotation_matrix(coords1_centered, coords2_centered)
    
    # Apply rotation and translation
    coords1_aligned = (R @ coords1_centered.T).T + center2
    
    # Calculate RMSD
    rmsd_value = rmsd(coords1_aligned, coords2)
    
    return coords1_aligned, rmsd_value

def random_rotation_matrix() -> Matrix3D:
    """Generate a random 3D rotation matrix.
    
    Returns:
        Matrix3D: Random 3x3 rotation matrix
    """
    # Generate random rotation matrix using QR decomposition
    H = np.eye(3)
    Q, R = np.linalg.qr(np.random.randn(3, 3))
    
    # Ensure we have a proper rotation matrix (det = +1)
    if np.linalg.det(Q) < 0:
        Q[:, 0] = -Q[:, 0]
    
    return Q

def rotation_matrix(axis: Vector3D, angle: float, degrees: bool = True) -> Matrix3D:
    """Generate a rotation matrix for rotation around an arbitrary axis.
    
    Args:
        axis: Rotation axis (3,)
        angle: Rotation angle
        degrees: If True, angle is in degrees; otherwise in radians
        
    Returns:
        Matrix3D: 3x3 rotation matrix
    """
    if degrees:
        angle = np.radians(angle)
    
    axis = np.asarray(axis)
    axis = axis / np.linalg.norm(axis)
    
    cos_theta = np.cos(angle)
    sin_theta = np.sin(angle)
    
    # Cross product matrix
    cross = np.array([
        [0, -axis[2], axis[1]],
        [axis[2], 0, -axis[0]],
        [-axis[1], axis[0], 0]
    ])
    
    # Rodrigues' rotation formula
    R = (cos_theta * np.eye(3) + 
         sin_theta * cross + 
         (1 - cos_theta) * np.outer(axis, axis))
    
    return R
