"""Main pipeline for macrocycle design."""

import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import json

from .rf_diffusion import RFdiffusionRunner, setup_rfdiffusion
from .af_design import AFDesigner, setup_colabdesign, analyze_design
from .relaxation import Relaxer, setup_pyrosetta
from ..config.settings import BinderDesignConfig

logger = logging.getLogger(__name__)

class DesignPipeline:
    """Main pipeline for macrocycle design."""
    
    def __init__(self, config: BinderDesignConfig):
        """Initialize the pipeline with configuration."""
        self.config = config
        self._setup_directories()
        self._setup_components()
    
    def _setup_directories(self):
        """Create necessary directories."""
        dirs = [
            self.config.output_dir,
            self.config.output_dir / "01_backbones",
            self.config.output_dir / "02_relaxed",
            self.config.output_dir / "03_designed",
            self.config.output_dir / "logs"
        ]
        
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def _setup_components(self):
        """Set up pipeline components."""
        # Set up RFdiffusion
        self.rfdiffusion = RFdiffusionRunner(self.config.rfdiffusion_dir)
        
        # Set up AlphaFold-Design
        setup_colabdesign()
        self.af_designer = AFDesigner(self.config.af_params_dir)
        
        # Set up PyRosetta
        setup_pyrosetta()
        self.relaxer = Relaxer(
            fast_relax=self.config.fast_relax,
            constraints=self.config.use_constraints
        )
    
    def run(self) -> Dict[str, Any]:
        """Run the complete design pipeline."""
        results = {
            "stages": {},
            "final_designs": []
        }
        
        try:
            # Stage 1: Generate backbones with RFdiffusion
            logger.info("Stage 1: Generating backbones with RFdiffusion")
            backbones = self._generate_backbones()
            results["stages"]["backbone_generation"] = {
                "num_generated": len(backbones),
                "backbone_files": [str(p) for p in backbones]
            }
            
            # Stage 2: Relax structures
            logger.info("Stage 2: Relaxing structures")
            relaxed = self._relax_structures(backbones)
            results["stages"]["relaxation"] = {
                "num_relaxed": len(relaxed),
                "relaxed_files": [str(p) for p in relaxed]
            }
            
            # Stage 3: Design sequences
            logger.info("Stage 3: Designing sequences")
            designs = self._design_sequences(relaxed)
            results["stages"]["sequence_design"] = {
                "num_designed": len(designs),
                "design_files": [str(p) for p in designs],
                "designs": []
            }
            
            # Analyze final designs
            for design_file in designs:
                analysis = analyze_design(
                    str(design_file),
                    target_chain=self.config.target_chain
                )
                results["stages"]["sequence_design"]["designs"].append({
                    "file": str(design_file),
                    "analysis": analysis
                })
            
            results["final_designs"] = [str(p) for p in designs]
            
            # Save results
            with open(self.config.output_dir / "design_results.json", "w") as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Pipeline completed successfully. Results saved to {self.config.output_dir}")
            return results
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            raise
    
    def _generate_backbones(self) -> List[Path]:
        """Generate backbones using RFdiffusion."""
        output_dir = self.config.output_dir / "01_backbones"
        
        # Download target PDB if needed
        target_pdb = self._get_target_pdb()
        
        # Generate backbones
        backbones = self.rfdiffusion.generate_backbones(
            pdb_path=str(target_pdb),
            output_dir=str(output_dir),
            pdb_id=self.config.pdb_id,
            target_chain=self.config.target_chain,
            binder_length=self.config.binder_length,
            num_designs=self.config.num_backbones,
            hotspots=self.config.hotspots
        )
        
        return [Path(p) for p in backbones]
    
    def _relax_structures(self, input_pdbs: List[Path]) -> List[Path]:
        """Relax generated structures."""
        output_dir = self.config.output_dir / "02_relaxed"
        relaxed_pdbs = []
        
        for i, pdb in enumerate(input_pdbs):
            if i >= self.config.top_k:
                break
                
            output_pdb = output_dir / f"relaxed_{i+1}.pdb"
            
            self.relaxer.relax_structure(
                input_pdb=str(pdb),
                output_pdb=str(output_pdb),
                target_chains=[self.config.target_chain],
                binder_chains=["B"],  # Assuming binder is chain B
                constrain_distance=self.config.constrain_distance
            )
            
            relaxed_pdbs.append(output_pdb)
        
        return relaxed_pdbs
    
    def _design_sequences(self, input_pdbs: List[Path]) -> List[Path]:
        """Design sequences for relaxed structures."""
        output_dir = self.config.output_dir / "03_designed"
        designed_pdbs = []
        
        for i, pdb in enumerate(input_pdbs):
            if i >= self.config.top_k:
                break
                
            output_prefix = output_dir / f"design_{i+1}"
            
            results = self.af_designer.design_sequence(
                pdb_path=str(pdb),
                output_dir=str(output_prefix.parent),
                target_chain=self.config.target_chain,
                binder_chains=["B"],  # Assuming binder is chain B
                num_seqs=1,
                num_recycles=self.config.num_recycles,
                iterations=self.config.design_iterations,
                temperature=self.config.temperature,
                fix_sequence=True,
                fix_backbone=False,
                cyclic=self.config.cyclic
            )
            
            if results["output_pdbs"]:
                designed_pdbs.append(Path(results["output_pdbs"][0]))
        
        return designed_pdbs
    
    def _get_target_pdb(self) -> Path:
        """Get the target PDB file, downloading if necessary."""
        pdb_dir = self.config.output_dir / "pdb"
        pdb_dir.mkdir(exist_ok=True)
        
        pdb_file = pdb_dir / f"{self.config.pdb_id}.pdb"
        
        if not pdb_file.exists():
            logger.info(f"Downloading PDB {self.config.pdb_id}...")
            import requests
            
            url = f"https://files.rcsb.org/download/{self.config.pdb_id}.pdb"
            response = requests.get(url)
            response.raise_for_status()
            
            with open(pdb_file, "wb") as f:
                f.write(response.content)
        
        return pdb_file

def run_pipeline(config: BinderDesignConfig) -> Dict[str, Any]:
    """Run the complete design pipeline.
    
    Args:
        config: Configuration for the pipeline
        
    Returns:
        Dictionary with pipeline results
    """
    pipeline = DesignPipeline(config)
    return pipeline.run()
