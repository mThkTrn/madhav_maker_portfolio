# Macrocycle Design Pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An end-to-end pipeline for de novo design of cyclic peptide binders.

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/macrocycle-design.git
cd macrocycle-design

# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### Dependencies

This package has the following core dependencies:
- Python 3.8+
- RFdiffusion (automatically installed)
- PyRosetta (automatically installed via pip)
- AlphaFold parameters (automatically downloaded)

## Quick Start

### Python API

```python
from macrocycle_design import BinderDesignConfig, run_design_pipeline

# Configure the pipeline
config = BinderDesignConfig(
    pdb_id="9BGH",           # Target PDB ID (KRAS)
    target_chain="A",        # Target chain in the PDB
    hotspots=[36, 62, 63],   # Known hotspot residues on KRAS (1-indexed)
    binder_length=25,        # Length of the cyclic peptide
    num_backbones=5,         # Number of backbones to generate
    top_k=3,                 # Number of designs to keep
    output_dir="output"      # Output directory (default: 'output')
)

# Run the complete pipeline
results = run_design_pipeline(config)
```


## Documentation

For detailed documentation, including API reference and advanced usage, please visit the project [GitHub](https://github.com/Ilovenewyork/macrocycle_design).

## Contributing

Contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please open an issue or contact [Madhavendra Thakur](mailto:madhavendra.thakur@gmail.com).