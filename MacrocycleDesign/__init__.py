"""
Macrocycle Design - A library for de novo design of cyclic protein binders.
"""

__version__ = "0.1.0"

from .config.settings import BinderDesignConfig
from .core.backbone_generation import generate_backbones
from .core.structure_selection import select_structures
from .core.relaxation import relax_structures
from .core.sequence_design import design_sequences

def run_design_pipeline(config):
    """Run the complete cyclic binder design pipeline.
    
    Args:
        config: BinderDesignConfig instance with all parameters
        
    Returns:
        dict: Results from each stage of the pipeline
    """
    results = {}
    
    # Generate backbones
    logger.info("Generating backbones...")
    backbones = generate_backbones(
        target_pdb=config.target_pdb,
        chain_id=config.chain_id,
        num_backbones=config.num_backbones,
        **config.backbone_generation_params
    )
    results['backbones'] = backbones
    
    # Select structures
    logger.info("Selecting structures...")
    selected = select_structures(
        backbones,
        selection_method=config.selection_method,
        **config.structure_selection_params
    )
    results['selected_structures'] = selected
    
    # Relax structures
    logger.info("Relaxing structures...")
    relaxed = relax_structures(
        selected,
        relax_method=config.relax_method,
        **config.relaxation_params
    )
    results['relaxed_structures'] = relaxed
    
    # Design sequences
    logger.info("Designing sequences...")
    designed = design_sequences(
        relaxed,
        design_method=config.design_method,
        **config.sequence_design_params
    )
    results['designed_sequences'] = designed
    
    return results
