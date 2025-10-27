"""Macrocycle Design: A Python library for de novo design of cyclic peptide binders.

This library provides tools and utilities for designing cyclic peptide binders
with applications in protein-protein interaction modulation.
"""

__version__ = "0.2.0"
__author__ = "Madhavendra Thakur"
__email__ = "madhavendra.thakur@gmail.com"
__license__ = "MIT"

# Import key components to make them easily accessible
from macrocycle_design.pipeline import BinderDesignConfig, DesignPipeline, run_design_pipeline

# Core functionality
from macrocycle_design.core import (
    # Core classes
    RFdiffusionRunner,
    AFDesigner,
    Relaxer,
    
    # Setup functions
    setup_environment,
    setup_rfdiffusion,
    setup_colabdesign,
    setup_pyrosetta,
    download_af_params,
)

# Utility functions
from macrocycle_design.core.structure_selection import find_interface_residues, select_top_designs

try:
    from macrocycle_design.utils.file_io import read_pdb, write_pdb
except ImportError:
    # Fallback if utils module is not available
    read_pdb = write_pdb = None

try:
    from macrocycle_design.utils.geometry import align_structures, rmsd
except ImportError:
    # Fallback if geometry module is not available
    align_structures = rmsd = None

__all__ = [
    # Configuration
    'BinderDesignConfig',
    
    # Pipeline
    'run_design_pipeline',
    'DesignPipeline',
    'setup_environment',
    
    # Core classes
    'RFdiffusionRunner',
    'AFDesigner',
    'Relaxer',
    
    # Core functions
    'find_interface_residues',
    'select_top_designs',
    'read_pdb',
    'write_pdb',
    'align_structures',
    'rmsd',
    
    # Setup functions
    'setup_rfdiffusion',
    'setup_colabdesign',
    'setup_pyrosetta',
    'download_af_params',
]
