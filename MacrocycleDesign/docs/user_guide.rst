User Guide
=========

This guide provides detailed information about using Macrocycle Design's features.

Backbone Generation
------------------
The ``backbone_generation`` module provides tools for creating cyclic peptide backbones.

### Basic Usage

.. code-block:: python

    from macrocycle_design.core.backbone_generation import BackboneGenerator
    
    # Initialize the generator
    generator = BackboneGenerator()
    
    # Generate a backbone for a sequence
    sequence = "ACDEFGHIKLMNPQRSTVWY"  # All 20 standard amino acids
    coords = generator.generate_cyclic_backbone(sequence, method='circular')
    
    # Save to PDB
    generator.sequence = sequence
    generator.coordinates = coords
    generator.save_pdb("peptide.pdb")

### Available Methods

1. **Circular Conformation**
   - Creates a planar circular peptide
   - Parameters: radius (default=5.0 Å)

2. **Helical Conformation**
   - Creates a helical peptide
   - Parameters: radius (default=2.5 Å), rise_per_residue (default=1.5 Å)

3. **Random Conformation**
   - Creates a random coil structure
   - Parameters: box_size (default=10.0 Å)

Structure Analysis
-----------------
The ``structure_selection`` module helps analyze protein structures and interfaces.

### Finding Interfaces

.. code-block:: python

    from macrocycle_design.core.structure_selection import StructureSelector
    
    # Initialize the selector
    selector = StructureSelector()
    
    # Load a structure
    struct_name = selector.load_structure("protein_complex.pdb")
    
    # Find interface between chains A and B
    interface = selector.find_protein_protein_interface(
        struct_name, "A", "B", distance_cutoff=5.0
    )
    
    # Identify hotspots
    hotspots = selector.identify_hotspots(interface)

### Selecting Binding Sites

.. code-block:: python

    # Select residues within 10Å of residue 50 in chain A
    binding_site = selector.select_binding_site(
        struct_name, "A", center_residue=50, radius=10.0
    )

File I/O Utilities
-----------------
The ``file_io`` module provides functions for reading and writing structure files.

### Reading PDB Files

.. code-block:: python

    from macrocycle_design.utils.file_io import read_pdb, write_pdb
    
    # Read a PDB file
    pdb_data = read_pdb("protein.pdb")
    
    # Access atom data
    for atom in pdb_data['atoms']:
        print(f"{atom['res_name']} {atom['res_seq']} {atom['name']}: {atom['x']}, {atom['y']}, {atom['z']}")

### Writing PDB Files

.. code-block:: python

    # Modify the structure data
    for atom in pdb_data['atoms']:
        if atom['name'] == 'CA':
            atom['x'] += 1.0  # Shift CA atoms by 1Å in x-direction
    
    # Write the modified structure
    write_pdb("modified.pdb", pdb_data)

Geometry Utilities
-----------------
The ``geometry`` module provides functions for geometric calculations.

### Basic Calculations

.. code-block:: python

    from macrocycle_design.utils.geometry import distance, angle, dihedral
    import numpy as np
    
    # Define points in 3D space
    p1 = np.array([0, 0, 0])
    p2 = np.array([1, 0, 0])
    p3 = np.array([1, 1, 0])
    p4 = np.array([1, 1, 1])
    
    # Calculate distances and angles
    d = distance(p1, p2)
    a = angle(p1, p2, p3)  # In degrees
    t = dihedral(p1, p2, p3, p4)  # In degrees

### Structure Alignment

.. code-block:: python

    from macrocycle_design.utils.geometry import align_structures, rmsd
    
    # Align two sets of coordinates
    aligned_coords, rmsd_value = align_structures(coords1, coords2)
    print(f"RMSD after alignment: {rmsd_value:.2f} Å")

Configuration
------------
Package-wide settings can be configured through the ``settings`` module.

.. code-block:: python

    from macrocycle_design.config import settings
    
    # Update settings
    settings.DEBUG = True
    settings.VERBOSE = True
    
    # Or update multiple settings at once
    settings.update({
        'MD_TEMPERATURE': 310.0,  # 37°C
        'MD_TIMESTEP': 0.002,     # 2 fs
    })
