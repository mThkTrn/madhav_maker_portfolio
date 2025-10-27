"""Backbone generation for macrocycle design.

This module provides functionality for generating and manipulating
backbone conformations of cyclic peptides.
"""

from typing import List, Tuple, Optional
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class BackboneGenerator:
    """Class for generating and manipulating cyclic peptide backbones."""
    
    def __init__(self):
        self.residues = []
        self.sequence = ""
        self.coordinates = None
        
    def generate_cyclic_backbone(self, sequence: str, method: str = 'circular') -> np.ndarray:
        """Generate a cyclic peptide backbone for the given sequence.
        
        Args:
            sequence: Amino acid sequence of the cyclic peptide
            method: Method for generating the backbone ('circular', 'helical', 'random')
            
        Returns:
            numpy.ndarray: Array of backbone coordinates (N, CA, C, O) for each residue
        """
        self.sequence = sequence.upper()
        n_residues = len(self.sequence)
        
        if method == 'circular':
            self._generate_circular_backbone(n_residues)
        elif method == 'helical':
            self._generate_helical_backbone(n_residues)
        elif method == 'random':
            self._generate_random_backbone(n_residues)
        else:
            raise ValueError(f"Unknown backbone generation method: {method}")
            
        return self.coordinates
    
    def _generate_circular_backbone(self, n_residues: int, radius: float = 5.0) -> None:
        """Generate a circular backbone conformation.
        
        Args:
            n_residues: Number of residues in the peptide
            radius: Radius of the circular conformation in Angstroms
        """
        angles = np.linspace(0, 2 * np.pi, n_residues, endpoint=False)
        x = radius * np.cos(angles)
        y = radius * np.sin(angles)
        z = np.zeros_like(x)
        
        # Create CA coordinates in a circle
        ca_coords = np.column_stack((x, y, z))
        
        # Generate N, C, O coordinates for each CA
        self._generate_backbone_atoms(ca_coords)
    
    def _generate_helical_backbone(self, n_residues: int, radius: float = 2.5, 
                                rise_per_residue: float = 1.5) -> None:
        """Generate a helical backbone conformation.
        
        Args:
            n_residues: Number of residues in the peptide
            radius: Radius of the helix in Angstroms
            rise_per_residue: Rise per residue along the helix axis in Angstroms
        """
        t = np.linspace(0, 2 * np.pi, n_residues, endpoint=False)
        x = radius * np.cos(t)
        y = radius * np.sin(t)
        z = rise_per_residue * np.arange(n_residues)
        
        # Center the helix
        z = z - np.mean(z)
        
        # Create CA coordinates in a helix
        ca_coords = np.column_stack((x, y, z))
        
        # Generate N, C, O coordinates for each CA
        self._generate_backbone_atoms(ca_coords)
    
    def _generate_random_backbone(self, n_residues: int, box_size: float = 10.0) -> None:
        """Generate a random backbone conformation within a box.
        
        Args:
            n_residues: Number of residues in the peptide
            box_size: Size of the bounding box in Angstroms
        """
        # Generate random CA coordinates within a box
        ca_coords = np.random.uniform(-box_size/2, box_size/2, (n_residues, 3))
        
        # Sort by z-coordinate to make the chain somewhat reasonable
        ca_coords = ca_coords[ca_coords[:, 2].argsort()]
        
        # Generate N, C, O coordinates for each CA
        self._generate_backbone_atoms(ca_coords)
    
    def _generate_backbone_atoms(self, ca_coords: np.ndarray) -> None:
        """Generate N, CA, C, O coordinates for each CA position.
        
        This is a simplified approach that places backbone atoms in a reasonable
        geometry relative to the CA positions.
        
        Args:
            ca_coords: Array of CA coordinates (n_residues x 3)
        """
        n_residues = len(ca_coords)
        
        # Calculate vectors between consecutive CAs
        if n_residues > 1:
            vecs = np.roll(ca_coords, -1, axis=0) - ca_coords
            vecs[-1] = ca_coords[0] - ca_coords[-1]  # Close the loop
        else:
            vecs = np.array([[1.0, 0.0, 0.0]])
        
        # Normalize vectors
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0  # Avoid division by zero
        vecs = vecs / norms
        
        # Generate perpendicular vectors
        perp_vecs = np.zeros_like(vecs)
        perp_vecs[:, 0] = -vecs[:, 1]
        perp_vecs[:, 1] = vecs[:, 0]
        
        # Normalize perpendicular vectors
        perp_norms = np.linalg.norm(perp_vecs, axis=1, keepdims=True)
        perp_norms[perp_norms == 0] = 1.0  # Avoid division by zero
        perp_vecs = perp_vecs / perp_norms
        
        # Set standard bond lengths (in Angstroms)
        ca_n_length = 1.46
        ca_c_length = 1.53
        c_o_length = 1.24
        
        # Generate N, C, O coordinates
        n_coords = ca_coords - 0.5 * ca_n_length * vecs + 0.5 * ca_n_length * perp_vecs
        c_coords = ca_coords + 0.5 * ca_c_length * vecs + 0.5 * ca_c_length * perp_vecs
        o_coords = c_coords + 0.7 * c_o_length * perp_vecs
        
        # Combine all coordinates (N, CA, C, O for each residue)
        self.coordinates = np.zeros((n_residues, 4, 3))
        self.coordinates[:, 0] = n_coords  # N
        self.coordinates[:, 1] = ca_coords  # CA
        self.coordinates[:, 2] = c_coords  # C
        self.coordinates[:, 3] = o_coords  # O
    
    def save_pdb(self, filename: str) -> None:
        """Save the current conformation to a PDB file.
        
        Args:
            filename: Output PDB filename
        """
        if self.coordinates is None:
            raise ValueError("No coordinates to save. Generate a backbone first.")
            
        with open(filename, 'w') as f:
            # Write header
            f.write("HEADER    CYCLIC PEPTIDE BACKBONE\n")
            f.write("COMPND    GENERATED BY MACROCYCLE_DESIGN\n")
            
            atom_num = 1
            for res_num, (res_name, res_coords) in enumerate(zip(self.sequence, self.coordinates), 1):
                # Write N atom
                f.write(f"ATOM  {atom_num:5d}  N   {res_name}  {res_num:4d}    "
                       f"{res_coords[0][0]:8.3f}{res_coords[0][1]:8.3f}{res_coords[0][2]:8.3f}  1.00  0.00           N\n")
                atom_num += 1
                
                # Write CA atom
                f.write(f"ATOM  {atom_num:5d}  CA  {res_name}  {res_num:4d}    "
                       f"{res_coords[1][0]:8.3f}{res_coords[1][1]:8.3f}{res_coords[1][2]:8.3f}  1.00  0.00           C\n")
                atom_num += 1
                
                # Write C atom
                f.write(f"ATOM  {atom_num:5d}  C   {res_name}  {res_num:4d}    "
                       f"{res_coords[2][0]:8.3f}{res_coords[2][1]:8.3f}{res_coords[2][2]:8.3f}  1.00  0.00           C\n")
                atom_num += 1
                
                # Write O atom
                f.write(f"ATOM  {atom_num:5d}  O   {res_name}  {res_num:4d}    "
                       f"{res_coords[3][0]:8.3f}{res_coords[3][1]:8.3f}{res_coords[3][2]:8.3f}  1.00  0.00           O\n")
                atom_num += 1
            
            # Write CONECT records for the peptide bonds
            for i in range(1, len(self.sequence) + 1):
                # Peptide bond: N(i) - C(i-1)
                n_atom = (i - 1) * 4 + 1
                c_prev = i * 4 - 2  # C of previous residue
                if i == 1:
                    c_prev = len(self.sequence) * 4 - 2  # Connect to last residue for cyclic
                f.write(f"CONECT{n_atom:5d}{c_prev:5d}\n")
                
                # CA-CA connection
                ca_atom = (i - 1) * 4 + 2
                ca_next = i * 4 + 2 if i < len(self.sequence) else 2  # Next CA or first CA for cyclic
                f.write(f"CONECT{ca_atom:5d}{ca_next:5d}\n")
            
            # Write footer
            f.write("TER\nEND\n")


def generate_cyclic_peptide(sequence: str, method: str = 'circular', 
                          output_pdb: Optional[str] = None) -> np.ndarray:
    """Convenience function to generate a cyclic peptide backbone.
    
    Args:
        sequence: Amino acid sequence of the cyclic peptide
        method: Method for generating the backbone ('circular', 'helical', 'random')
        output_pdb: Optional PDB filename to save the structure
        
    Returns:
        numpy.ndarray: Array of backbone coordinates (N, CA, C, O) for each residue
    """
    generator = BackboneGenerator()
    coords = generator.generate_cyclic_backbone(sequence, method=method)
    
    if output_pdb:
        generator.save_pdb(output_pdb)
        
    return coords
