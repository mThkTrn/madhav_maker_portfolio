from setuptools import setup, find_packages
import os

# Read the README for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="macrocycle-design",
    version="0.2.15",
    description="An end-to-end pipeline for de novo design of cyclic peptide binders",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Madhavendra Thakur",
    author_email="madhavendra.thakur@gmail.com",
    url="https://github.com/yourusername/kras-binder-pipeline",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies
        'numpy>=1.20.0',
        'biopython>=1.79',
        'pandas>=1.3.0',
        'matplotlib>=3.4.0',
        'tqdm>=4.65.0',
        'requests>=2.28.0',
        'pyyaml>=6.0',
        'loguru>=0.7.0',
        
        # Structure analysis
        'prody>=2.0.0',
        'nglview>=3.0.0',
        'mdtraj>=1.9.0',
        
        # Machine learning
        'torch>=1.12.0',
        'torchvision>=0.13.0',
        'torchaudio>=0.12.0',
        'transformers>=4.25.0',
        
        # Structure prediction and design
        'colabdesign>=1.1.1',
        'pyrosetta>=2022.0',
        
        # Utilities
        'pytest>=7.0.0',
        'pytest-cov>=4.0.0',
        'black>=22.0.0',
        'isort>=5.10.0',
        'mypy>=0.990',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'isort>=5.10.0',
            'mypy>=0.990',
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.0.0',
        ],
        'docs': [
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.0.0',
            'sphinx-autodoc-typehints>=1.19.0',
            'myst-parser>=0.18.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'macrocycle-design=macrocycle_design.cli:main',
        ],
    },
    include_package_data=True,
    package_data={
        'macrocycle_design': ['data/*.pdb', 'data/*.csv'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Chemistry',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    license="MIT License",
    keywords=[
        'protein-design',
        'computational-biology',
        'drug-discovery',
        'machine-learning',
        'bioinformatics',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/kras-binder-pipeline/issues',
        'Source': 'https://github.com/yourusername/kras-binder-pipeline',
        'Documentation': 'https://github.com/yourusername/kras-binder-pipeline#readme',
    },
)
