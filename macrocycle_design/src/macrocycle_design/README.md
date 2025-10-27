# Macrocycle Design Pipeline

An end-to-end pipeline for designing cyclic peptide binders using RFdiffusion, PyRosetta, and AlphaFold-Design.

## Features

- **Backbone Generation**: Generate cyclic peptide backbones using RFdiffusion
- **Structure Relaxation**: Optimize structures with PyRosetta
- **Sequence Design**: Design sequences using AlphaFold-Design
- **Easy Integration**: Simple Python API for pipeline control

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/kras-binder-pipeline.git
   cd kras-binder-pipeline
   ```

2. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Quick Start

```python
from macrocycle_design import BinderDesignConfig, run_design_pipeline

# Configure the pipeline
config = BinderDesignConfig(
    pdb_id="9BGH",
    target_chain="A",
    hotspots=[36, 62, 63],
    binder_length=25,
    num_backbones=20,
    top_k=5,
    output_dir="output"
)

# Run the complete pipeline
results = run_design_pipeline(config)
```

## Pipeline Stages

1. **Backbone Generation**: Uses RFdiffusion to generate cyclic peptide backbones
2. **Structure Selection**: Selects top backbones based on scoring
3. **Relaxation**: Optimizes structures using PyRosetta
4. **Sequence Design**: Designs sequences using AlphaFold-Design

## Dependencies

- Python 3.8+
- RFdiffusion
- PyRosetta
- AlphaFold-Design (ColabDesign)
- See `setup.py` for Python dependencies

## License

MIT

## Citation

If you use this code in your research, please cite:

```
@software{macrocycle_design_2023,
  author = {Your Name},
  title = {Macrocycle Design Pipeline},
  year = {2023},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/yourusername/kras-binder-pipeline}}
}
```
