Examples
========

This page contains practical examples demonstrating how to use Macrocycle Design for various tasks.

Example 1: Designing a Cyclic Peptide Binder
-------------------------------------------
This example shows how to design a cyclic peptide that could bind to a target protein.

.. code-block:: python

    import nglview as nv
    from macrocycle_design.core.backbone_generation import generate_cyclic_peptide
    from macrocycle_design.core.structure_selection import StructureSelector
    
    # Generate a cyclic peptide with a specific sequence
    sequence = "ACDEFGH"
    coords = generate_cyclic_peptide(sequence, method='circular', output_pdb="peptide.pdb")
    
    # Load the target protein
    selector = StructureSelector()
    target = selector.load_structure("target_protein.pdb")
    
    # Visualize the peptide and target
    view = nv.show_file("peptide.pdb")
    view.add_component("target_protein.pdb")
    view.add_representation("cartoon", selection="not hetero")
    view.add_representation("licorice", selection=sequence)
    view

Example 2: Analyzing Protein-Protein Interfaces
----------------------------------------------
This example demonstrates how to analyze and visualize protein-protein interfaces.

.. code-block:: python

    from IPython.display import display
    import pandas as pd
    from macrocycle_design.core.structure_selection import StructureSelector
    
    # Initialize the selector and load the complex
    selector = StructureSelector()
    complex_name = selector.load_structure("protein_complex.pdb")
    
    # Find interface between chains A and B
    interface = selector.find_protein_protein_interface(
        complex_name, "A", "B", distance_cutoff=5.0
    )
    
    # Convert interface data to a pandas DataFrame for better visualization
    df = pd.DataFrame(interface['residues'])
    display(df[['chain', 'resnum', 'resname', 'contacts']].head())
    
    # Visualize the interface
    view = nv.show_file("protein_complex.pdb")
    view.clear_representations()
    view.add_representation("cartoon")
    
    # Highlight interface residues
    for res in interface['residues']:
        view.add_representation("licorice", 
                             selection=f"{res['chain']} and {res['resnum']}")
    
    view

Example 3: Structure Alignment
----------------------------
This example shows how to align two similar protein structures.

.. code-block:: python

    import numpy as np
    from macrocycle_design.utils.geometry import align_structures, rmsd
    from macrocycle_design.utils.file_io import read_pdb
    
    # Read two PDB files
    pdb1 = read_pdb("structure1.pdb")
    pdb2 = read_pdb("structure2.pdb")
    
    # Extract CA coordinates
    def get_ca_coords(pdb_data):
        return np.array([[a['x'], a['y'], a['z']] 
                        for a in pdb_data['atoms'] 
                        if a['name'] == 'CA'])
    
    coords1 = get_ca_coords(pdb1)
    coords2 = get_ca_coords(pdb2)
    
    # Align structures
    aligned_coords, rmsd_value = align_structures(coords1, coords2)
    print(f"RMSD: {rmsd_value:.2f} Å")

Example 4: Generating a Library of Conformations
----------------------------------------------
This example demonstrates generating multiple conformations of the same peptide.

.. code-block:: python

    from macrocycle_design.core.backbone_generation import BackboneGenerator
    import numpy as np
    
    # Initialize the generator
    generator = BackboneGenerator()
    sequence = "ACDEF"
    
    # Generate multiple conformations
    n_conformations = 5
    conformations = []
    
    for i in range(n_conformations):
        # Use different methods or parameters
        method = 'circular' if i % 2 == 0 else 'helical'
        coords = generator.generate_cyclic_backbone(
            sequence, 
            method=method,
            radius=4.0 + np.random.random() * 2.0  # Random radius between 4.0 and 6.0 Å
        )
        conformations.append(coords)
    
    # Save conformations
    for i, coords in enumerate(conformations):
        generator.sequence = sequence
        generator.coordinates = coords
        generator.save_pdb(f"conformation_{i+1}.pdb")

Example 5: Calculating Geometric Properties
-----------------------------------------
This example shows how to calculate various geometric properties of a peptide.

.. code-block:: python

    from macrocycle_design.utils.geometry import (
        distance, angle, dihedral, 
        center_of_mass, radius_of_gyration
    )
    import numpy as np
    
    # Example coordinates (N, CA, C, O atoms for one residue)
    residue = np.array([
        [0.0, 1.0, 0.0],  # N
        [1.0, 0.0, 0.0],  # CA
        [2.0, 0.5, 0.0],  # C
        [2.5, 1.5, 0.0]   # O
    ])
    
    # Calculate bond length (N-CA)
    bond_length = distance(residue[0], residue[1])
    
    # Calculate bond angle (N-CA-C)
    bond_angle = angle(residue[0], residue[1], residue[2])
    
    # Calculate dihedral angle (N-CA-C-O)
    dihedral_angle = dihedral(*residue)
    
    # Calculate center of mass (assuming equal masses)
    com = center_of_mass(residue)
    
    # Calculate radius of gyration
    rg = radius_of_gyration(residue)
    
    print(f"Bond length (N-CA): {bond_length:.3f} Å")
    print(f"Bond angle (N-CA-C): {bond_angle:.1f}°")
    print(f"Dihedral angle (N-CA-C-O): {dihedral_angle:.1f}°")
    print(f"Center of mass: {com}")
    print(f"Radius of gyration: {rg:.3f} Å")
