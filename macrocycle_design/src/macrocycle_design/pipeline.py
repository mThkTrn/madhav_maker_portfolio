"""Main pipeline for the macrocycle design workflow."""

import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum, auto

from macrocycle_design.core import (
    RFdiffusionRunner, AFDesigner, Relaxer,
    setup_environment
)

logger = logging.getLogger(__name__)

class DesignStage(Enum):
    """Pipeline stages for tracking progress."""
    INIT = auto()
    BACKBONE_GENERATION = auto()
    STRUCTURE_SELECTION = auto()
    RELAXATION = auto()
    SEQUENCE_DESIGN = auto()
    COMPLETED = auto()

@dataclass
class BinderDesignConfig:
    """Configuration for the binder design pipeline."""
    # Target information
    pdb_id: str = "9BGH"
    target_chain: str = "A"
    hotspots: List[int] = field(default_factory=lambda: [36, 62, 63])
    
    # Binder parameters
    binder_length: int = 25
    num_backbones: int = 20
    top_k: int = 5
    
    # Output directories
    output_dir: str = "pipeline_out"
    rfdiffusion_dir: str = "RFdiffusion"
    af_params_dir: str = "params"
    
    # RFdiffusion settings
    diffusion_steps: int = 100
    
    # Relaxation settings
    fast_relax: bool = True
    use_constraints: bool = True
    constrain_distance: float = 8.0
    
    # Sequence design settings
    design_iterations: int = 10
    num_recycles: int = 3
    temperature: float = 0.4
    
    # Runtime settings
    verbose: bool = True
    save_intermediates: bool = True
    device: str = "cuda:0"
    
    def __post_init__(self):
        """Post-initialization setup."""
        # Create output directories
        self.output_dir = Path(self.output_dir)
        self.dirs = {
            "bb": self.output_dir / "01_backbones",
            "topk": self.output_dir / "02_top5",
            "relax": self.output_dir / "03_relaxed_complex",
            "monos": self.output_dir / "04_binder_monomers",
            "af": self.output_dir / "05_afdesign",
        }
        
        for d in self.dirs.values():
            d.mkdir(parents=True, exist_ok=True)

class DesignPipeline:
    """Main pipeline for designing macrocycle binders."""
    
    def __init__(self, config: Optional[BinderDesignConfig] = None):
        """Initialize the pipeline with the given configuration."""
        self.config = config or BinderDesignConfig()
        self.stage = DesignStage.INIT
        self.results = {}
    
    def run(self) -> Dict[str, Any]:
        """Run the complete design pipeline."""
        try:
            # Set up environment
            self._log("Setting up environment...")
            setup_environment()
            
            # Generate backbones
            self._log("Generating backbones with RFdiffusion...")
            self._generate_backbones()
            
            # Select top backbones
            self._log("Selecting top backbones...")
            self._select_top_backbones()
            
            # Relax structures
            self._log("Relaxing structures...")
            self._relax_structures()
            
            # Design sequences
            self._log("Designing sequences...")
            self._design_sequences()
            
            self.stage = DesignStage.COMPLETED
            self._log("Pipeline completed successfully!")
            
            return self.results
            
        except Exception as e:
            self._log(f"Pipeline failed at stage {self.stage}: {e}", level="error")
            raise
    
    def _generate_backbones(self):
        """Generate initial backbones using RFdiffusion."""
        self.stage = DesignStage.BACKBONE_GENERATION
        
        # Initialize RFdiffusion
        rfdiffusion = RFdiffusionRunner(
            pdb_id=self.config.pdb_id,
            target_chain=self.config.target_chain,
            hotspots=self.config.hotspots,
            binder_length=self.config.binder_length,
            num_designs=self.config.num_backbones,
            output_dir=str(self.config.dirs["bb"]),
            verbose=self.config.verbose
        )
        
        # Run backbone generation
        self.results["backbone_pdbs"] = rfdiffusion.run()
    
    def _select_top_backbones(self):
        """Select top backbones based on scoring."""
        self.stage = DesignStage.STRUCTURE_SELECTION
        
        # In a real implementation, this would involve scoring and filtering
        # For now, just copy the first top_k backbones
        src_dir = self.config.dirs["bb"]
        dst_dir = self.config.dirs["topk"]
        
        top_pdbs = []
        for i, pdb_file in enumerate(sorted(src_dir.glob("*.pdb"))):
            if i >= self.config.top_k:
                break
            dst_file = dst_dir / f"top_{i+1}.pdb"
            shutil.copy(pdb_file, dst_file)
            top_pdbs.append(str(dst_file))
        
        self.results["top_backbones"] = top_pdbs
    
    def _relax_structures(self):
        """Relax the selected structures."""
        self.stage = DesignStage.RELAXATION
        
        relaxer = Relaxer(
            fast_relax=self.config.fast_relax,
            use_constraints=self.config.use_constraints,
            constrain_distance=self.config.constrain_distance
        )
        
        relaxed_pdbs = []
        for pdb_file in self.results["top_backbones"]:
            output_file = self.config.dirs["relax"] / f"relaxed_{Path(pdb_file).name}"
            relaxed_pdb = relaxer.relax(
                str(pdb_file),
                output_file=str(output_file),
                target_chain=self.config.target_chain,
                binder_chain="B"
            )
            relaxed_pdbs.append(relaxed_pdb)
        
        self.results["relaxed_pdbs"] = relaxed_pdbs
    
    def _design_sequences(self):
        """Design sequences for the relaxed structures."""
        self.stage = DesignStage.SEQUENCE_DESIGN
        
        designer = AFDesigner(
            params_dir=self.config.af_params_dir,
            design_iterations=self.config.design_iterations,
            num_recycles=self.config.num_recycles,
            temperature=self.config.temperature,
            verbose=self.config.verbose
        )
        
        designed_pdbs = []
        for pdb_file in self.results["relaxed_pdbs"]:
            output_dir = self.config.dirs["af"] / Path(pdb_file).stem
            output_dir.mkdir(exist_ok=True)
            
            designed = designer.design_sequence(
                str(pdb_file),
                output_dir=str(output_dir),
                target_chain=self.config.target_chain,
                binder_chain="B"
            )
            designed_pdbs.extend(designed)
        
        self.results["designed_pdbs"] = designed_pdbs
    
    def _log(self, message: str, level: str = "info"):
        """Log a message with the current stage."""
        if self.stage != DesignStage.INIT:
            message = f"[{self.stage.name}] {message}"
        
        if level.lower() == "info":
            logger.info(message)
        elif level.lower() == "warning":
            logger.warning(message)
        elif level.lower() == "error":
            logger.error(message)
        else:
            logger.debug(message)

def run_design_pipeline(config: Optional[BinderDesignConfig] = None) -> Dict[str, Any]:
    """Run the complete design pipeline with the given configuration.
    
    Args:
        config: Configuration for the pipeline. If None, default config is used.
        
    Returns:
        Dictionary containing pipeline results
    """
    pipeline = DesignPipeline(config)
    return pipeline.run()
