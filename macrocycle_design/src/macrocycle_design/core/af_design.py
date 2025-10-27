"""AlphaFold-Design integration for sequence design."""

import os
import subprocess
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class AFDesigner:
    """Class for designing sequences using AlphaFold-Design."""
    
    def __init__(self, params_dir: str = "params", **kwargs):
        """Initialize the AlphaFold-Design runner.
        
        Args:
            params_dir: Directory containing AlphaFold parameters
            **kwargs: Additional arguments for design
        """
        self.params_dir = Path(params_dir).resolve()
        self._check_installation()
        
        # Design parameters
        self.design_iterations = kwargs.get('design_iterations', 10)
        self.num_recycles = kwargs.get('num_recycles', 3)
        self.temperature = kwargs.get('temperature', 0.4)
        self.verbose = kwargs.get('verbose', True)
    
    def _check_installation(self):
        """Verify AlphaFold and ColabDesign are properly installed."""
        try:
            import colabdesign
        except ImportError:
            raise ImportError(
                "ColabDesign not found. Please install it with: "
                "pip install git+https://github.com/sokrypton/ColabDesign.git@v1.1.1"
            )
        
        if not self.params_dir.exists():
            raise FileNotFoundError(
                f"AlphaFold parameters not found at {self.params_dir}. "
                "Please download them first."
            )
    
    def design_sequence(
        self,
        input_pdb: str,
        output_dir: str,
        target_chain: str = "A",
        binder_chain: str = "B",
        num_designs: int = 5,
    ) -> List[str]:
        """Design sequences for a given binder backbone.
        
        Args:
            input_pdb: Path to input PDB file
            output_dir: Directory to save outputs
            target_chain: Chain ID of the target protein
            binder_chain: Chain ID of the binder
            num_designs: Number of designs to generate
            
        Returns:
            List of paths to designed PDB files
        """
        try:
            import colabdesign as cd
            from colabdesign.af.alphafold.common import protein
            from colabdesign.af.alphafold.model import model
            from colabdesign.af.alphafold.model import config
            from colabdesign.af.alphafold.model import data
            from colabdesign.af.alphafold.common import residue_constants
            
            # Set up output directory
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Load the input structure
            with open(input_pdb, 'r') as f:
                pdb_str = f.read()
            
            # Initialize the design model
            design_model = cd.afdesign.AFDesign(
                initial_guess=True,
                use_multimer=True,
                data_dir=str(self.params_dir),
                num_recycles=self.num_recycles,
                model_names=['model_1', 'model_2', 'model_3', 'model_4', 'model_5'],
                verbose=self.verbose
            )
            
            # Prepare the design
            design_model.prep_inputs(
                pdb_str,
                chain=target_chain,
                rm_aa='C',  # Disallow cysteine to prevent disulfides
                fix_seq=False
            )
            
            # Run the design
            design_model.design(
                num_seqs=num_designs,
                num_iterations=self.design_iterations,
                temperature=self.temperature,
                keep_best=True,
                verbose=self.verbose
            )
            
            # Save the designs
            output_files = []
            for i, (seq, pdb_str) in enumerate(zip(design_model.sequences, design_model.save_pdb())):
                output_file = output_dir / f"design_{i+1}.pdb"
                with open(output_file, 'w') as f:
                    f.write(pdb_str)
                output_files.append(str(output_file))
            
            return output_files
            
        except Exception as e:
            logger.error(f"Error in sequence design: {e}", exc_info=True)
            raise

def setup_colabdesign():
    """Set up ColabDesign and download required parameters."""
    try:
        # Install ColabDesign if not already installed
        subprocess.run(
            ["pip", "install", "git+https://github.com/sokrypton/ColabDesign.git@v1.1.1"],
            check=True
        )
        
        # Create params directory if it doesn't exist
        params_dir = Path("params")
        params_dir.mkdir(exist_ok=True)
        
        # Download AlphaFold parameters if needed
        param_file = params_dir / "params_model_1.npz"
        if not param_file.exists():
            print("Downloading AlphaFold parameters...")
            subprocess.run(
                ["wget", "-q", "https://storage.googleapis.com/alphafold/alphafold_params_2022-12-06.tar"],
                check=True
            )
            subprocess.run(
                ["tar", "-xf", "alphafold_params_2022-12-06.tar", "-C", str(params_dir)],
                check=True
            )
            os.remove("alphafold_params_2022-12-06.tar")
            
    except Exception as e:
        logger.error(f"Error setting up ColabDesign: {e}", exc_info=True)
        raise
