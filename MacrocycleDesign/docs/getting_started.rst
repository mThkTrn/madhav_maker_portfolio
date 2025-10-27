Getting Started
==============

This guide will help you get started with Macrocycle Design by walking through some basic examples.

Basic Concepts
--------------
Macrocycle Design is a Python package for designing and analyzing cyclic peptides. The main components are:

- **Backbone Generation**: Create 3D structures of cyclic peptides
- **Structure Selection**: Analyze protein structures and interfaces
- **Utilities**: Helper functions for file I/O and geometric calculations

Your First Macrocycle
---------------------
Let's create a simple cyclic peptide:

.. code-block:: python

    from macrocycle_design.core.backbone_generation import generate_cyclic_peptide
    
    # Generate a cyclic peptide with sequence ACD
    coords = generate_cyclic_peptide("ACD", method='circular', output_pdb="my_peptide.pdb")
    print(f"Generated peptide with {len(coords)} residues")

This will create a PDB file named "my_peptide.pdb" containing your cyclic peptide.

Analyzing a Protein Interface
----------------------------
Let's analyze a protein-protein interface:

.. code-block:: python

    from macrocycle_design.core.structure_selection import find_interface_residues
    
    # Analyze the interface between chains A and B in a PDB file
    interface = find_interface_residues("protein_complex.pdb", "A", "B")
    
    print(f"Found {len(interface['residues'])} interface residues")
    for res in interface['residues']:
        print(f"Chain {res['chain']}, Residue {res['resnum']} ({res['resname']})")

Visualizing Structures
---------------------
You can visualize the generated structures using NGLView:

.. code-block:: python

    import nglview as nv
    
    # View the generated peptide
    view = nv.show_file("my_peptide.pdb")
    view.add_representation("ball+stick")
    view

Next Steps
----------
- Explore the :doc:`user_guide` for detailed usage instructions
- Check out the :doc:`examples` for more complex use cases
- Refer to the :doc:`api` for complete API documentation
