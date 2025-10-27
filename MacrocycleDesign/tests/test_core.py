"""Tests for the core functionality of macrocycle_design."""

import unittest
import numpy as np
from pathlib import Path
import tempfile

from macrocycle_design.core.backbone_generation import BackboneGenerator, generate_cyclic_peptide
from macrocycle_design.core.structure_selection import StructureSelector


class TestBackboneGeneration(unittest.TestCase):
    """Tests for backbone generation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.sequence = "ACDEFGHIKLMNPQRSTVWY"  # All 20 standard amino acids
        self.generator = BackboneGenerator()

    def test_generate_circular_backbone(self):
        """Test generation of circular backbone."""
        coords = self.generator.generate_cyclic_backbone(self.sequence, method='circular')
        self.assertEqual(coords.shape, (20, 4, 3))  # 20 residues, 4 atoms each, 3D coords
        
        # Check that the first and last residues are close in space (circular)
        first_ca = coords[0, 1]  # CA of first residue
        last_ca = coords[-1, 1]  # CA of last residue
        distance = np.linalg.norm(first_ca - last_ca)
        self.assertLess(distance, 10.0)  # Should be close in a circular conformation

    def test_generate_helical_backbone(self):
        """Test generation of helical backbone."""
        coords = self.generator.generate_cyclic_backbone(self.sequence, method='helical')
        self.assertEqual(coords.shape, (20, 4, 3))
        
        # Check that the z-coordinate increases (helix goes up)
        z_coords = coords[:, 1, 2]  # Z-coordinates of CA atoms
        self.assertGreater(z_coords[-1], z_coords[0])

    def test_save_pdb(self):
        """Test saving backbone to PDB file."""
        coords = self.generator.generate_cyclic_backbone("ACD")
        with tempfile.NamedTemporaryFile(suffix='.pdb', delete=False) as tmp:
            tmp_path = tmp.name
            
        try:
            self.generator.sequence = "ACD"
            self.generator.coordinates = coords
            self.generator.save_pdb(tmp_path)
            
            # Check that the file was created and has content
            self.assertTrue(Path(tmp_path).exists())
            self.assertGreater(Path(tmp_path).stat().st_size, 0)
            
            # Check that the file contains expected content
            with open(tmp_path, 'r') as f:
                content = f.read()
                self.assertIn('HEADER', content)
                self.assertIn('ATOM', content)
                self.assertIn('TER', content)
                self.assertIn('END', content)
        finally:
            # Clean up
            Path(tmp_path).unlink(missing_ok=True)

    def test_generate_cyclic_peptide_function(self):
        """Test the convenience function for generating cyclic peptides."""
        with tempfile.NamedTemporaryFile(suffix='.pdb', delete=False) as tmp:
            tmp_path = tmp.name
            
        try:
            coords = generate_cyclic_peptide("ACD", output_pdb=tmp_path)
            self.assertEqual(coords.shape, (3, 4, 3))  # 3 residues, 4 atoms each, 3D coords
            self.assertTrue(Path(tmp_path).exists())
        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestStructureSelection(unittest.TestCase):
    """Tests for structure selection functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.selector = StructureSelector()
        
        # Create a temporary PDB file for testing
        self.temp_pdb = Path("test.pdb")
        with open(self.temp_pdb, 'w') as f:
            f.write("""HEADER    TEST
ATOM      1  N   ALA A   1       0.000   0.000   0.000  1.00  0.00           N
ATOM      2  CA  ALA A   1       1.458   0.000   0.000  1.00  0.00           C
ATOM      3  C   ALA A   1       2.009   1.420   0.000  1.00  0.00           C
ATOM      4  O   ALA A   1       1.251   2.381   0.000  1.00  0.00           O
ATOM      5  CB  ALA A   1       1.991  -0.773  -1.214  1.00  0.00           C
ATOM      6  N   GLY B   1       3.332   1.537   0.000  1.00  0.00           N
ATOM      7  CA  GLY B   1       4.009   2.819   0.000  1.00  0.00           C
ATOM      8  C   GLY B   1       5.523   2.819   0.000  1.00  0.00           C
ATOM      9  O   GLY B   1       6.191   1.782   0.000  1.00  0.00           O
END
""")

    def tearDown(self):
        """Clean up test fixtures."""
        if self.temp_pdb.exists():
            self.temp_pdb.unlink()

    def test_load_structure(self):
        """Test loading a structure from a PDB file."""
        struct_name = self.selector.load_structure(str(self.temp_pdb))
        self.assertEqual(struct_name, self.temp_pdb.stem)
        self.assertIn(struct_name, self.selector.structures)

    def test_find_protein_protein_interface(self):
        """Test finding a protein-protein interface."""
        struct_name = self.selector.load_structure(str(self.temp_pdb))
        interface = self.selector.find_protein_protein_interface(struct_name, 'A', 'B')
        
        self.assertEqual(interface['chains'], ('A', 'B'))
        self.assertGreater(len(interface['residues']), 0)
        
        # Check that the interface contains residues from both chains
        chains = {res['chain'] for res in interface['residues']}
        self.assertTrue({'A', 'B'}.issubset(chains))

    def test_identify_hotspots(self):
        """Test identifying hotspot residues."""
        struct_name = self.selector.load_structure(str(self.temp_pdb))
        interface = self.selector.find_protein_protein_interface(struct_name, 'A', 'B')
        hotspots = self.selector.identify_hotspots(interface)
        
        self.assertGreater(len(hotspots), 0)
        self.assertIn('score', hotspots[0])
        self.assertIn('resnum', hotspots[0])
        self.assertIn('chain', hotspots[0])


if __name__ == '__main__':
    unittest.main()
