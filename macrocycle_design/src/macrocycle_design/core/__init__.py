"""Core functionality for macrocycle design.

This package contains the core modules for the macrocycle design pipeline,
including structure manipulation, energy calculations, and optimization routines.
"""

# Core modules
from macrocycle_design.core.backbone_generation import *  # noqa
from macrocycle_design.core.structure_selection import *  # noqa
from macrocycle_design.core.rf_diffusion import RFdiffusionRunner, setup_rfdiffusion  # noqa
from macrocycle_design.core.af_design import AFDesigner, setup_colabdesign  # noqa
from macrocycle_design.core.relaxation import Relaxer, setup_pyrosetta  # noqa

# Main pipeline function
def setup_environment():
    """Set up the complete environment with all required tools."""
    setup_pyrosetta()
    setup_colabdesign()
    setup_rfdiffusion()

__all__ = [
    # Modules
    'backbone_generation',
    'structure_selection',
    'rf_diffusion',
    'af_design',
    'relaxation',
    
    # Main classes
    'RFdiffusionRunner',
    'AFDesigner',
    'Relaxer',
    
    # Setup functions
    'setup_environment',
    'setup_rfdiffusion',
    'setup_colabdesign',
    'setup_pyrosetta',
    'download_af_params',
]
