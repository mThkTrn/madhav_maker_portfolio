"""AlphaFold-Design integration for sequence design."""

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging
import numpy as np
import pandas as pd
from Bio.PDB import PDBParser

logger = logging.getLogger(__name__)

def setup_colabdesign(install_dir: str = "colabdesign"):
    """Set up ColabDesign installation if needed.
    
    Args:
        install_dir: Directory to install ColabDesign in
    """
    install_dir = Path(install_dir)
    
    if not install_dir.exists():
        logger.info("Installing ColabDesign...")
        subprocess.run([
            "pip", "install", "-q", 
            "git+https://github.com/sokrypton/ColabDesign.git@v1.1.1"
        ], check=True)

def validate_af_params(params_dir: str) -> None:
    """Validate that required AlphaFold parameters exist.
    
    Args:
        params_dir: Directory containing AlphaFold parameters
        
    Raises:
        FileNotFoundError: If required parameter files are missing
    """
    params_dir = Path(params_dir)
    required_files = ["params_model_1_multimer.npz"]
    
    for f in required_files:
        if not (params_dir / f).exists():
            raise FileNotFoundError(
                f"Required AlphaFold parameter file not found: {params_dir/f}\n"
                "Please download AlphaFold parameters and provide the correct path."
            )

class AFDesigner:
    """Class to handle sequence design using AlphaFold-Design."""
    
    def __init__(self, params_dir: str = "params"):
        """Initialize with path to AlphaFold parameters."""
        self.params_dir = Path(params_dir).resolve()
        self._check_setup()
    
    def _check_setup(self):
        """Verify AlphaFold-Design is properly set up."""
        required_params = [
            self.params_dir / "params_model_1_multimer.npz",
            self.params_dir / "params_model_2_multimer.npz",
            self.params_dir / "params_model_3_multimer.npz",
            self.params_dir / "params_model_4_multimer.npz",
            self.params_dir / "params_model_5_multimer.npz"
        ]
        
        for f in required_params:
            if not f.exists():
                raise FileNotFoundError(
                    f"Required AlphaFold parameter file not found: {f}\n"
                    "Please download AlphaFold parameters first."
                )
    
    def design_sequence(
        self,
        pdb_path: str,
        output_dir: str,
        target_chain: str = "A",
        binder_chains: Optional[List[str]] = None,
        num_seqs: int = 1,
        num_recycles: int = 3,
        iterations: int = 10,
        temperature: float = 0.4,
        fix_sequence: bool = True,
        fix_backbone: bool = False,
        cyclic: bool = True,
    ) -> Dict[str, Any]:
        """Design sequences using AlphaFold-Design.
        
        Args:
            pdb_path: Path to input PDB file
            output_dir: Directory to save outputs
            target_chain: Chain ID of the target protein
            binder_chains: List of chain IDs for the binder (if None, infer from PDB)
            num_seqs: Number of sequences to generate
            num_recycles: Number of recycles during inference
            iterations: Number of optimization iterations
            temperature: Temperature for sampling
            fix_sequence: Whether to fix the target sequence
            fix_backbone: Whether to fix the backbone during design
            cyclic: Whether the binder is cyclic
            
        Returns:
            Dictionary containing design results
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Import ColabDesign here to avoid early import issues
        try:
            import colabdesign as cd
            from colabdesign.af.alphafold.models import mk_af_serial
            from colabdesign.shared.protein import mk_af_init_sequence
            from colabdesign.af.alphafold.common import protein
            from colabdesign.af.alphafold.model import model
        except ImportError as e:
            raise ImportError(
                "ColabDesign not found. Please install it first using setup_colabdesign()."
            ) from e
        
        # Set up the design model
        design_model = cd.afdesign.AFDesign(
            initial_weights="multimer",
            params_dir=str(self.params_dir),
            use_multimer=True,
            data_dir=str(self.params_dir.parent)
        )
        
        # Prepare the input structure
        design_model.prep_input(
            pdb_filename=str(pdb_path),
            chain=target_chain,
            fix_pos=None if fix_sequence else [],
            fix_aa=None if fix_sequence else "X",
            rm_aa="C" if not cyclic else None,
            symmetry=1,
            verbose=True
        )
        
        # Set up the design parameters
        design_model.set_opt(
            num_seqs=num_seqs,
            num_recycles=num_recycles,
            iterations=iterations,
            temperature=temperature,
            fix_sequence=fix_sequence,
            fix_backbone=fix_backbone,
            design_cyclic=cyclic
        )
        
        # Run the design
        logger.info("Running AlphaFold-Design...")
        design_model.design_3stage()
        
        # Save the results
        results = {
            "sequences": design_model.aux["seq"],
            "scores": design_model.aux["score"],
            "plddts": design_model.aux["plddt"],
            "output_pdbs": []
        }
        
        # Save the designed structures
        for i, (seq, plddt) in enumerate(zip(results["sequences"], results["plddts"])):
            output_pdb = output_dir / f"design_{i+1}_plddt{plddt:.2f}.pdb"
            design_model.save_current_pdb(fname=str(output_pdb))
            results["output_pdbs"].append(str(output_pdb))
        
        return results

def analyze_design(pdb_path: str, target_chain: str = "A") -> Dict[str, Any]:
    """Analyze a designed structure.
    
    Args:
        pdb_path: Path to the designed PDB file
        target_chain: Chain ID of the target protein
        
    Returns:
        Dictionary with analysis results
    """
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("design", pdb_path)
    
    # Calculate basic metrics
    model = structure[0]
    target = model[target_chain]
    
    # Get binder chains (all non-target chains)
    binder_chains = [chain for chain in model if chain.id != target_chain]
    
    # Calculate contacts
    def get_atoms(chain):
        return [atom for atom in chain.get_atoms() if atom.get_name() == "CA"]
    
    target_atoms = get_atoms(target)
    binder_atoms = []
    for chain in binder_chains:
        binder_atoms.extend(get_atoms(chain))
    
    # Calculate distances
    contacts = 0
    min_dist = float('inf')
    
    for ta in target_atoms:
        for ba in binder_atoms:
            dist = np.linalg.norm(ta.coord - ba.coord)
            if dist < 8.0:  # Contact cutoff
                contacts += 1
            if dist < min_dist:
                min_dist = dist
    
    # Calculate RMSD (placeholder - would need reference structure)
    rmsd = 0.0  # Not calculated here
    
    return {
        "num_contacts": contacts,
        "min_distance": min_dist,
        "rmsd": rmsd,
        "binder_chains": [c.id for c in binder_chains],
        "target_length": len(target),
        "binder_lengths": [len(c) for c in binder_chains]
    }
