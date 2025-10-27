import unittest
import macrocycle_design

class TestImport(unittest.TestCase):
    """Test that the package can be imported."""

    def test_import(self):
        """Test that the package can be imported."""
        self.assertIsNotNone(macrocycle_design.__version__)
        self.assertIsNotNone(macrocycle_design.__author__)

if __name__ == '__main__':
    unittest.main()
