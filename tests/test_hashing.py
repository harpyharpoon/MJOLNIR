import unittest
import tempfile
import os
import json
import shutil
from unittest.mock import patch, mock_open, MagicMock
import sys

# Add the parent directory to the path to import mjolnir modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock tkinter and pyudev imports to avoid dependency issues in tests
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.simpledialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['pyudev'] = MagicMock()

from mjolnir.hashing import hash_file, generate_baseline, compare_with_baseline


class TestHashing(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment before each test."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_file.txt")
        with open(self.test_file, "w") as f:
            f.write("test content")
    
    def tearDown(self):
        """Clean up test environment after each test."""
        shutil.rmtree(self.test_dir)
    
    def test_hash_file_success(self):
        """Test that hash_file correctly hashes a file."""
        # Create a test file with known content
        test_content = "Hello, World!"
        with open(self.test_file, "w") as f:
            f.write(test_content)
        
        # Calculate expected SHA256 hash
        import hashlib
        expected_hash = hashlib.sha256(test_content.encode()).hexdigest()
        
        # Test the function
        result = hash_file(self.test_file)
        self.assertEqual(result, expected_hash)
    
    def test_hash_file_nonexistent(self):
        """Test that hash_file handles non-existent files gracefully."""
        nonexistent_file = os.path.join(self.test_dir, "nonexistent.txt")
        
        with patch('mjolnir.hashing.log') as mock_log:
            result = hash_file(nonexistent_file)
            self.assertIsNone(result)
            mock_log.assert_called_once()
    
    def test_hash_file_permission_error(self):
        """Test that hash_file handles permission errors gracefully."""
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with patch('mjolnir.hashing.log') as mock_log:
                result = hash_file(self.test_file)
                self.assertIsNone(result)
                mock_log.assert_called_once()
    
    @patch('mjolnir.hashing.get_baseline_hash_file')
    @patch('mjolnir.hashing.get_mandatory_files')
    @patch('mjolnir.hashing.log')
    def test_generate_baseline_success(self, mock_log, mock_get_files, mock_get_baseline):
        """Test successful baseline generation."""
        # Mock the configuration
        mock_get_baseline.return_value = os.path.join(self.test_dir, "baseline.json")
        mock_get_files.return_value = {
            "TEST": [self.test_file]
        }
        
        # Run the function
        generate_baseline()
        
        # Verify baseline file was created
        baseline_file = mock_get_baseline.return_value
        self.assertTrue(os.path.exists(baseline_file))
        
        # Verify content is correct
        with open(baseline_file, "r") as f:
            baseline_data = json.load(f)
        
        self.assertIn("TEST", baseline_data)
        self.assertIn(self.test_file, baseline_data["TEST"])
        self.assertIsNotNone(baseline_data["TEST"][self.test_file])
        
        # Verify log was called
        mock_log.assert_called()
    
    @patch('mjolnir.hashing.get_baseline_hash_file')
    @patch('mjolnir.hashing.get_mandatory_files')
    @patch('mjolnir.hashing.log')
    def test_generate_baseline_with_directory(self, mock_log, mock_get_files, mock_get_baseline):
        """Test baseline generation with directories."""
        # Create a test directory with files
        test_subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(test_subdir)
        test_subfile = os.path.join(test_subdir, "subfile.txt")
        with open(test_subfile, "w") as f:
            f.write("sub content")
        
        mock_get_baseline.return_value = os.path.join(self.test_dir, "baseline.json")
        mock_get_files.return_value = {
            "TEST_DIR": [self.test_dir]
        }
        
        generate_baseline()
        
        # Verify baseline includes files from directory
        with open(mock_get_baseline.return_value, "r") as f:
            baseline_data = json.load(f)
        
        self.assertIn("TEST_DIR", baseline_data)
        # Should include both the original test file and the subdirectory file
        self.assertGreaterEqual(len(baseline_data["TEST_DIR"]), 2)
    
    @patch('mjolnir.hashing.get_baseline_hash_file')
    @patch('mjolnir.hashing.get_mandatory_files')
    @patch('mjolnir.hashing.log')
    def test_compare_with_baseline_no_baseline(self, mock_log, mock_get_files, mock_get_baseline):
        """Test comparison when no baseline exists."""
        mock_get_baseline.return_value = os.path.join(self.test_dir, "nonexistent_baseline.json")
        
        compare_with_baseline()
        
        mock_log.assert_called_with("[!] No baseline hash file found.")
    
    @patch('mjolnir.hashing.get_baseline_hash_file')
    @patch('mjolnir.hashing.get_mandatory_files')
    @patch('mjolnir.hashing.log')
    def test_compare_with_baseline_match(self, mock_log, mock_get_files, mock_get_baseline):
        """Test comparison when files match baseline."""
        # Create baseline file
        baseline_file = os.path.join(self.test_dir, "baseline.json")
        file_hash = hash_file(self.test_file)
        baseline_data = {
            "TEST": {
                self.test_file: file_hash
            }
        }
        with open(baseline_file, "w") as f:
            json.dump(baseline_data, f)
        
        mock_get_baseline.return_value = baseline_file
        mock_get_files.return_value = {
            "TEST": [self.test_file]
        }
        
        compare_with_baseline()
        
        # Should log that all files match
        mock_log.assert_called_with("All mandatory files match baseline.")
    
    @patch('mjolnir.hashing.get_baseline_hash_file')
    @patch('mjolnir.hashing.get_mandatory_files')
    @patch('mjolnir.hashing.log')
    def test_compare_with_baseline_mismatch(self, mock_log, mock_get_files, mock_get_baseline):
        """Test comparison when files don't match baseline."""
        # Create baseline file with different hash
        baseline_file = os.path.join(self.test_dir, "baseline.json")
        baseline_data = {
            "TEST": {
                self.test_file: "different_hash"
            }
        }
        with open(baseline_file, "w") as f:
            json.dump(baseline_data, f)
        
        mock_get_baseline.return_value = baseline_file
        mock_get_files.return_value = {
            "TEST": [self.test_file]
        }
        
        compare_with_baseline()
        
        # Should log mismatches detected
        mock_log.assert_any_call("[!] Hash mismatches detected:")


if __name__ == '__main__':
    unittest.main()
