"""RFdiffusion integration for generating cyclic peptide backbones."""

import os
import subprocess
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class RFdiffusionRunner:
    """Class to handle RFdiffusion execution for cyclic peptide design."""
    
    def __init__(self, rfdiffusion_dir: str = "RFdiffusion"):
        """Initialize with path to RFdiffusion installation."""
        self.rfdiffusion_dir = Path(rfdiffusion_dir).resolve()
        self.models_dir = self.rfdiffusion_dir / "models"
        self._check_installation()
    
    def _check_installation(self):
        """Verify RFdiffusion is properly installed."""
        required_files = [
            self.rfdiffusion_dir / "scripts/run_inference.py",
            self.models_dir / "Base_ckpt.pt",
            self.models_dir / "Complex_base_ckpt.pt"
        ]
        
        for f in required_files:
            if not f.exists():
                raise FileNotFoundError(
                    f"Required RFdiffusion file not found: {f}\n"
                    "Please install RFdiffusion first."
                )
    
    def generate_backbones(
        self,
        pdb_path: str,
        output_dir: str,
        pdb_id: str = "9BGH",
        target_chain: str = "A",
        binder_length: int = 25,
        num_designs: int = 20,
        hotspots: Optional[List[int]] = None,
    ) -> List[str]:
        """Generate cyclic peptide backbones using RFdiffusion.
        
        Args:
            pdb_path: Path to input PDB file
            output_dir: Directory to save outputs
            pdb_id: PDB ID of the target
            target_chain: Chain ID to target
            binder_length: Length of the cyclic peptide
            num_designs: Number of designs to generate
            hotspots: List of hotspot residue numbers (1-based)
            
        Returns:
            List of paths to generated PDB files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_prefix = output_dir / "bb"
        
        # Format contigs and hotspots for RFdiffusion
        contigs = f"{target_chain}2-168/0 {binder_length}"
        hotspot_str = "[" + ",".join([f"{target_chain}{h}" for h in (hotspots or [])]) + "]"
        
        # Set up potentials
        potentials = [
            f"type:interface_ncontacts,binderlen:{binder_length},weight:5,r_0:8,d_0:4",
            f"type:binder_ncontacts,binderlen:{binder_length},weight:2,r_0:8,d_0:4",
            f"type:binder_ROG,binderlen:{binder_length},weight:3,min_dist:15",
        ]
        potentials_arg = 'potentials.guiding_potentials=["' + '","'.join(potentials) + '"]'
        
        # Set up environment
        env = os.environ.copy()
        env["HYDRA_FULL_ERROR"] = "1"
        env["PYTHONPATH"] = str(self.rfdiffusion_dir) + os.pathsep + env.get("PYTHONPATH", "")
        
        # Build command
        cmd = [
            "python", "scripts/run_inference.py", "--config-name", "base",
            "hydra.run.dir=.",
            f"inference.output_prefix={output_prefix}",
            f"inference.num_designs={num_designs}",
            f"inference.input_pdb={pdb_path}",
            "inference.cyclic=True",
            f"inference.cyc_chains={target_chain}",
            f"ppi.hotspot_res={hotspot_str}",
            f"contigmap.contigs=[ {contigs} ]",
            "inference.write_trajectory=True",
            potentials_arg,
            "potentials.guide_scale=5",
            "potentials.guide_decay=quadratic",
        ]
        
        # Run RFdiffusion
        logger.info("Running RFdiffusion...")
        logger.debug("Command: %s", " ".join(cmd))
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.rfdiffusion_dir),
                env=env,
                check=True,
                capture_output=True,
                text=True
            )
            logger.debug("RFdiffusion output:\n%s", result.stdout)
            
            # Return list of generated PDB files
            return sorted(output_dir.glob("*.pdb"))
            
        except subprocess.CalledProcessError as e:
            logger.error("RFdiffusion failed with error:")
            logger.error(e.stderr)
            raise RuntimeError(f"RFdiffusion failed: {e}")


def setup_rfdiffusion(install_dir: str = "RFdiffusion") -> RFdiffusionRunner:
    """Set up RFdiffusion installation if needed.
    
    Args:
        install_dir: Directory to install RFdiffusion in
        
    Returns:
        Configured RFdiffusionRunner instance
    """
    install_dir = Path(install_dir)
    
    if not install_dir.exists():
        logger.info("Cloning RFdiffusion repository...")
        subprocess.run(["git", "clone", "https://github.com/RosettaCommons/RFdiffusion.git", str(install_dir)], 
                      check=True)
        
        logger.info("Installing dependencies...")
        subprocess.run(["pip", "install", "jedi", "omegaconf", "hydra-core", "icecream", 
                       "pyrsistent", "pynvml", "decorator"], check=True)
        subprocess.run(["pip", "install", "--no-dependencies", "dgl==2.0.0", 
                       "-f", "https://data.dgl.ai/wheels/cu121/repo.html"], check=True)
        subprocess.run(["pip", "install", "--no-dependencies", "e3nn==0.5.5", "opt_einsum_fx"], 
                      check=True)
        subprocess.run(["python", "-m", "pip", "install", str(install_dir / "env/SE3Transformer/")], 
                      check=True)
    
    models_dir = install_dir / "models"
    models_dir.mkdir(exist_ok=True)
    
    # Download required models
    model_files = {
        "Base_ckpt.pt": "http://files.ipd.uw.edu/pub/RFdiffusion/6f5902ac237024bdd0c176cb93063dc4/Base_ckpt.pt",
        "Complex_base_ckpt.pt": "http://files.ipd.uw.edu/pub/RFdiffusion/e29311f6f1bf1af907f9ef9f44b8328b/Complex_base_ckpt.pt"
    }
    
    for filename, url in model_files.items():
        if not (models_dir / filename).exists():
            logger.info("Downloading %s...", filename)
            subprocess.run(["wget", "-q", "-O", str(models_dir / filename), url], check=True)
    
    return RFdiffusionRunner(str(install_dir))
