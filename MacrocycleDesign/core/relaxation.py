"""PyRosetta integration for structure relaxation."""

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

def setup_pyrosetta():
    """Set up PyRosetta installation if needed."""
    try:
        import pyrosetta  # noqa: F401
    except ImportError:
        logger.info("Installing PyRosetta...")
        subprocess.run([
            "pip", "install", "-q", 
            "pyrosetta-installer", 
            "pyrosetta-distributed",
            "biotite",
            "biopython",
            "numpy",
            "pandas"
        ], check=True)
        
        # Install PyRosetta
        import pyrosetta_installer
        pyrosetta_installer.install_pyrosetta()

class Relaxer:
    """Class to handle structure relaxation using PyRosetta."""
    
    def __init__(self, fast_relax: bool = True, constraints: bool = True):
        """Initialize the relaxer.
        
        Args:
            fast_relax: Whether to use FastRelax (True) or just Minimization (False)
            constraints: Whether to use constraints during relaxation
        """
        try:
            import pyrosetta
            from pyrosetta import rosetta
            self.pyrosetta = pyrosetta
            self.rosetta = rosetta
        except ImportError as e:
            raise ImportError(
                "PyRosetta not found. Please install it first using setup_pyrosetta()."
            ) from e
            
        self.fast_relax = fast_relax
        self.constraints = constraints
        self._init_rosetta()
    
    def _init_rosetta(self):
        """Initialize PyRosetta options."""
        options = [
            "-ignore_unrecognized_res 1",
            "-ignore_zero_occupancy false",
            "-load_PDB_components false",
            "-relax:constrain_relax_to_start_coords true",
            "-relax:coord_constrain_sidechains true",
            "-relax:ramp_constraints false",
            "-default_max_cycles 200",
            "-relax:min_type lbfgs_armijo_nonmonotone",
            "-out:level 200"
        ]
        
        if self.fast_relax:
            options.extend([
                "-relax:default_repeats 5",
                "-relax:ramp_constraints true"
            ])
        
        self.pyrosetta.init(" ".join(options))
    
    def relax_structure(
        self,
        input_pdb: str,
        output_pdb: str,
        target_chains: Optional[List[str]] = None,
        binder_chains: Optional[List[str]] = None,
        constrain_distance: float = 8.0,
    ) -> Dict[str, Any]:
        """Relax a protein structure.
        
        Args:
            input_pdb: Path to input PDB file
            output_pdb: Path to save relaxed PDB file
            target_chains: List of target chain IDs to fix during relaxation
            binder_chains: List of binder chain IDs to relax
            constrain_distance: Distance cutoff for constraints (Å)
            
        Returns:
            Dictionary with relaxation results
        """
        # Initialize pose
        pose = self.pyrosetta.pose_from_file(input_pdb)
        scorefxn = self.rosetta.core.scoring.get_score_function()
        
        # Set up constraints if needed
        if self.constraints:
            self._setup_constraints(pose, target_chains, binder_chains, constrain_distance)
        
        # Set up movemap
        movemap = self._create_movemap(pose, target_chains, binder_chains)
        
        # Run relaxation
        start_score = scorefxn(pose)
        
        if self.fast_relax:
            relax = self.rosetta.protocols.relax.FastRelax()
            relax.set_scorefxn(scorefxn)
            relax.cartesian(True)
            relax.min_type("lbfgs_armijo_nonmonotone")
            relax.set_movemap(movemap)
            relax.apply(pose)
        else:
            # Simple minimization
            min_mover = self.rosetta.protocols.minimization_packing.MinMover()
            min_mover.movemap(movemap)
            min_mover.score_function(scorefxn)
            min_mover.min_type("lbfgs_armijo_nonmonotone")
            min_mover.cartesian(True)
            min_mover.tolerance(0.1)
            min_mover.apply(pose)
        
        end_score = scorefxn(pose)
        
        # Save the relaxed structure
        pose.dump_pdb(output_pdb)
        
        return {
            "input_pdb": input_pdb,
            "output_pdb": output_pdb,
            "initial_score": start_score,
            "final_score": end_score,
            "score_delta": end_score - start_score
        }
    
    def _setup_constraints(
        self, 
        pose, 
        target_chains: Optional[List[str]],
        binder_chains: Optional[List[str]],
        distance: float
    ) -> None:
        """Set up constraints for relaxation."""
        if target_chains is None or binder_chains is None:
            return
            
        # Create constraint set
        cst_set = self.rosetta.core.scoring.constraints.ConstraintSet()
        
        # Get residue selectors
        target_selector = self.rosetta.core.select.residue_selector.ChainSelector(
            "".join(target_chains)
        )
        binder_selector = self.rosetta.core.select.residue_selector.ChainSelector(
            "".join(binder_chains)
        )
        
        # Get CA atoms
        target_ca = []
        binder_ca = []
        
        for i in range(1, pose.size() + 1):
            if target_selector.apply(pose, i):
                target_ca.append(pose.residue(i).atom_index("CA"))
            elif binder_selector.apply(pose, i):
                binder_ca.append(pose.residue(i).atom_index("CA"))
        
        # Add distance constraints
        for t_idx in target_ca:
            for b_idx in binder_ca:
                # Create harmonic constraint for CA-CA distance
                func = self.rosetta.core.scoring.func.HarmonicFunc(distance, 1.0)
                cst = self.rosetta.core.scoring.constraints.AtomPairConstraint(
                    self.rosetta.core.id.AtomID(t_idx, 0),
                    self.rosetta.core.id.AtomID(b_idx, 0),
                    func
                )
                cst_set.add_constraint(cst)
        
        # Apply constraints to pose
        pose.add_constraints(cst_set.get_all_constraints())
    
    def _create_movemap(
        self, 
        pose,
        target_chains: Optional[List[str]],
        binder_chains: Optional[List[str]]
    ) -> Any:
        """Create a movemap for relaxation."""
        movemap = self.rosetta.core.kinematics.MoveMap()
        
        # Default: everything is fixed
        movemap.set_bb(False)
        movemap.set_chi(False)
        movemap.set_jump(False)
        
        # Allow binder chains to move
        if binder_chains:
            for i in range(1, pose.size() + 1):
                chain = pose.pdb_info().chain(i)
                if chain in binder_chains:
                    movemap.set_bb(i, True)
                    movemap.set_chi(i, True)
        
        return movemap

def relax_pdb(
    input_pdb: str,
    output_pdb: str,
    target_chains: Optional[List[str]] = None,
    binder_chains: Optional[List[str]] = None,
    fast_relax: bool = True,
    constraints: bool = True,
    constrain_distance: float = 8.0,
) -> Dict[str, Any]:
    """Convenience function to relax a PDB file.
    
    Args:
        input_pdb: Path to input PDB file
        output_pdb: Path to save relaxed PDB file
        target_chains: List of target chain IDs to fix during relaxation
        binder_chains: List of binder chain IDs to relax
        fast_relax: Whether to use FastRelax (True) or just Minimization (False)
        constraints: Whether to use constraints during relaxation
        constrain_distance: Distance cutoff for constraints (Å)
        
    Returns:
        Dictionary with relaxation results
    """
    relaxer = Relaxer(fast_relax=fast_relax, constraints=constraints)
    return relaxer.relax_structure(
        input_pdb=input_pdb,
        output_pdb=output_pdb,
        target_chains=target_chains,
        binder_chains=binder_chains,
        constrain_distance=constrain_distance
    )
