"""PyRosetta integration for structure relaxation."""

import os
import subprocess
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
import tempfile

logger = logging.getLogger(__name__)

class Relaxer:
    """Class for relaxing protein structures using PyRosetta."""
    
    def __init__(
        self,
        fast_relax: bool = True,
        use_constraints: bool = True,
        constrain_distance: float = 8.0,
        **kwargs
    ):
        """Initialize the relaxer.
        
        Args:
            fast_relax: Whether to use FastRelax (True) or just MinMover (False)
            use_constraints: Whether to apply constraints during relaxation
            constrain_distance: Distance (in Angstroms) for constraints
            **kwargs: Additional PyRosetta options
        """
        self.fast_relax = fast_relax
        self.use_constraints = use_constraints
        self.constrain_distance = constrain_distance
        self.extra_options = kwargs
        
        # Check PyRosetta installation
        self._check_installation()
    
    def _check_installation(self):
        """Verify PyRosetta is properly installed."""
        try:
            import pyrosetta
            self.pyrosetta = pyrosetta
            self.rosetta = pyrosetta.rosetta
        except ImportError:
            raise ImportError(
                "PyRosetta not found. Please install it with: "
                "pip install pyrosetta_installer pyrosetta-distributed"
            )
    
    def relax(
        self,
        input_pdb: str,
        output_pdb: Optional[str] = None,
        target_chain: str = "A",
        binder_chain: str = "B",
        cycles: int = 5,
    ) -> str:
        """Relax a protein structure.
        
        Args:
            input_pdb: Path to input PDB file
            output_pdb: Path to save relaxed structure (default: input_pdb + '_relaxed.pdb')
            target_chain: Chain ID of the target protein
            binder_chain: Chain ID of the binder
            cycles: Number of relaxation cycles
            
        Returns:
            Path to the relaxed PDB file
        """
        try:
            import pyrosetta
            from pyrosetta import rosetta
            from pyrosetta.rosetta import core, protocols
            
            # Set up output path
            if output_pdb is None:
                output_pdb = str(Path(input_pdb).with_stem(Path(input_pdb).stem + "_relaxed"))
            
            # Initialize PyRosetta with options
            options = [
                "-ignore_unrecognized_res",
                "-ignore_zero_occupancy false",
                "-ex1",
                "-ex2",
                "-use_input_sc",
                "-flip_HNQ",
                "-no_optH false",
                "-relax:default_repeats 5",
                "-default_max_cycles 200",
                "-relax:ramp_constraints false",
            ]
            
            if self.use_constraints:
                options.extend([
                    "-constraints:cst_fa_file",
                    "constraints.cst",
                    "-constraints:cst_fa_weight 1.0"
                ])
            
            # Initialize PyRosetta
            pyrosetta.init(" ".join(options))
            
            # Load the pose
            pose = pyrosetta.pose_from_pdb(input_pdb)
            
            # Set up constraints if needed
            if self.use_constraints:
                self._setup_constraints(pose, target_chain, binder_chain)
            
            # Set up score function
            scorefxn = rosetta.core.scoring.get_score_function()
            
            # Set up movemap (only allow binder to move)
            movemap = rosetta.core.kinematics.MoveMap()
            for i in range(1, pose.size() + 1):
                chain = pose.pdb_info().chain(i)
                if chain == binder_chain:
                    movemap.set_bb(i, True)
                    movemap.set_chi(i, True)
                else:
                    movemap.set_bb(i, False)
                    movemap.set_chi(i, False)
            
            # Run FastRelax or MinMover
            if self.fast_relax:
                relax = protocols.relax.FastRelax(scorefxn, cycles)
                relax.set_movemap(movemap)
                relax.apply(pose)
            else:
                min_mover = protocols.minimization_packing.MinMover()
                min_mover.score_function(scorefxn)
                min_mover.movemap(movemap)
                min_mover.min_type("lbfgs_armijo_nonmonotone")
                min_mover.tolerance(0.00025)
                min_mover.apply(pose)
            
            # Save the relaxed structure
            pose.dump_pdb(output_pdb)
            
            return output_pdb
            
        except Exception as e:
            logger.error(f"Error during relaxation: {e}", exc_info=True)
            raise
    
    def _setup_constraints(
        self,
        pose,
        target_chain: str = "A",
        binder_chain: str = "B",
    ) -> None:
        """Set up constraints between target and binder."""
        from pyrosetta.rosetta import core, protocols
        import math
        
        # Get residue ranges for target and binder
        target_residues = []
        binder_residues = []
        
        for i in range(1, pose.size() + 1):
            chain = pose.pdb_info().chain(i)
            if chain == target_chain:
                target_residues.append(i)
            elif chain == binder_chain:
                binder_residues.append(i)
        
        if not target_residues or not binder_residues:
            logger.warning("Could not find both target and binder chains for constraints")
            return
        
        # Create constraint set
        cst_set = core.scoring.constraints.ConstraintSet()
        
        # Add distance constraints between target and binder
        for t in target_residues[:10]:  # Limit to first 10 residues to avoid too many constraints
            for b in binder_residues[:10]:
                # Get CA atoms
                t_ca = pose.residue(t).atom("CA")
                b_ca = pose.residue(b).atom("CA")
                
                # Calculate distance
                distance = (t_ca.xyz() - b_ca.xyz()).norm()
                
                # Only add constraints for residues within cutoff
                if distance <= self.constrain_distance:
                    # Create a harmonic constraint
                    func = core.scoring.constraints.HarmonicFunc(
                        distance,  # x0 (target distance)
                        1.0,       # sd (standard deviation)
                    )
                    
                    # Create atom pair constraint
                    apc = core.scoring.constraints.AtomPairConstraint(
                        core.id.AtomID(t_ca.index(), t),
                        core.id.AtomID(b_ca.index(), b),
                        func
                    )
                    
                    cst_set.add_constraint(apc)
        
        # Add constraints to pose
        if cst_set.size() > 0:
            pose.add_constraints(cst_set)
            logger.info(f"Added {cst_set.size()} distance constraints")
        else:
            logger.warning("No distance constraints were added")

def setup_pyrosetta():
    """Set up PyRosetta installation."""
    try:
        # Check if PyRosetta is already installed
        import pyrosetta
        return
    except ImportError:
        pass
    
    try:
        # Install PyRosetta
        subprocess.run(
            ["pip", "install", "pyrosetta_installer", "pyrosetta-distributed"],
            check=True
        )
        
        # Import and run the installer
        import pyrosetta_installer as p
        p.install_pyrosetta()
        
        logger.info("PyRosetta installed successfully")
        
    except Exception as e:
        logger.error(f"Error installing PyRosetta: {e}", exc_info=True)
        raise
