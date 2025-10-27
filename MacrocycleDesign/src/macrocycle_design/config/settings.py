"""Settings and configuration for macrocycle_design.

This module provides a centralized configuration system for the macrocycle_design package.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum


class DesignStage(str, Enum):
    """Pipeline stages for macrocycle design."""
    BACKBONE_GEN = "backbone_generation"
    RELAXATION = "relaxation"
    SEQUENCE_DESIGN = "sequence_design"
    ALL = "all"


@dataclass
class BinderDesignConfig:
    """Configuration for the macrocycle design pipeline."""
    
    # Target protein settings
    pdb_id: str = "9BGH"
    target_chain: str = "A"
    hotspots: List[int] = field(default_factory=lambda: [36, 62, 63])
    
    # Binder settings
    binder_length: int = 25
    num_backbones: int = 20
    top_k: int = 5
    cyclic: bool = True
    
    # Output settings
    output_dir: Union[str, Path] = "output"
    rfdiffusion_dir: Union[str, Path] = "RFdiffusion"
    af_params_dir: Union[str, Path] = "params"
    
    # RFdiffusion settings
    diffusion_steps: int = 100
    diffusion_noise: float = 0.1
    
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
    overwrite: bool = False
    
    # Advanced settings
    device: str = "cuda:0"  # or "cpu"
    seed: Optional[int] = 42
    
    def __post_init__(self):
        """Convert string paths to Path objects and validate settings."""
        self.output_dir = Path(self.output_dir).resolve()
        self.rfdiffusion_dir = Path(self.rfdiffusion_dir).resolve()
        self.af_params_dir = Path(self.af_params_dir).resolve()
        
        # Validate settings
        if self.top_k > self.num_backbones:
            self.top_k = self.num_backbones
        
        if not self.hotspots:
            self.hotspots = []
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)


class Settings:
    """Global settings for the macrocycle_design package."""
    
    def __init__(self):
        # Core settings
        self.DEBUG: bool = False
        self.VERBOSE: bool = False
        
        # File paths
        self.PACKAGE_DIR: Path = Path(__file__).parent.parent.parent
        self.DATA_DIR: Path = self.PACKAGE_DIR / "data"
        self.OUTPUT_DIR: Path = self.PACKAGE_DIR / "outputs"
        
        # Ensure directories exist
        self.DATA_DIR.mkdir(exist_ok=True)
        self.OUTPUT_DIR.mkdir(exist_ok=True)
        
        # Update from environment variables
        self._update_from_env()
    
    def _update_from_env(self) -> None:
        """Update settings from environment variables."""
        # Debug mode
        if os.getenv('MACROCYCLE_DESIGN_DEBUG'):
            self.DEBUG = True
        
        # Verbose mode
        if os.getenv('MACROCYCLE_DESIGN_VERBOSE'):
            self.VERBOSE = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to a dictionary."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    def update(self, settings_dict: Dict[str, Any]) -> None:
        """Update settings from a dictionary."""
        for key, value in settings_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __str__(self) -> str:
        """Return a string representation of the settings."""
        return "\n".join(f"{k}: {v}" for k, v in self.to_dict().items())
    
    def __repr__(self) -> str:
        """Return a string representation of the settings object."""
        return f"<Settings: {len(self.to_dict())} parameters>"


# Create a global settings instance
settings = Settings()

__all__ = ['Settings', 'settings']
