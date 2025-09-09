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

from mjolnir.hashing import hash_file, generate_baseline, compare_with_baseline, generate_consolidated_hash, save_consolidated_hash, verify_consolidated_hash, get_hash_summary


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
    
    @patch('mjolnir.hashing.get_baseline_hash_file')
    @patch('mjolnir.hashing.log')
    def test_generate_consolidated_hash_no_baseline(self, mock_log, mock_get_baseline):
        """Test consolidated hash generation when no baseline exists."""
        mock_get_baseline.return_value = os.path.join(self.test_dir, "nonexistent_baseline.json")
        
        result = generate_consolidated_hash()
        
        self.assertIsNone(result)
        mock_log.assert_called_with("[!] No baseline hash file found. Generate baseline first.")
    
    @patch('mjolnir.hashing.get_baseline_hash_file')
    @patch('mjolnir.hashing.log')
    def test_generate_consolidated_hash_success(self, mock_log, mock_get_baseline):
        """Test successful consolidated hash generation."""
        # Create baseline file
        baseline_file = os.path.join(self.test_dir, "baseline.json")
        baseline_data = {
            "TEST": {
                "/path/file1.txt": "hash1",
                "/path/file2.txt": "hash2"
            },
            "OTHER": {
                "/other/file3.txt": "hash3"
            }
        }
        with open(baseline_file, "w") as f:
            json.dump(baseline_data, f)
        
        mock_get_baseline.return_value = baseline_file
        
        result = generate_consolidated_hash()
        
        self.assertIsNotNone(result)
        self.assertIn("master_hash", result)
        self.assertIn("file_count", result)
        self.assertIn("hash_list", result)
        self.assertEqual(result["file_count"], 3)
        self.assertEqual(len(result["hash_list"]), 3)
        
        # Verify hash list is sorted consistently
        expected_list = [
            "/other/file3.txt:hash3",
            "/path/file1.txt:hash1", 
            "/path/file2.txt:hash2"
        ]
        self.assertEqual(result["hash_list"], expected_list)
    
    @patch('mjolnir.hashing.get_baseline_hash_file')
    @patch('mjolnir.config.get_usb_mount')
    @patch('mjolnir.hashing.log')
    def test_save_consolidated_hash_success(self, mock_log, mock_get_mount, mock_get_baseline):
        """Test successful consolidated hash saving."""
        # Create baseline file
        baseline_file = os.path.join(self.test_dir, "baseline.json")
        baseline_data = {
            "TEST": {
                self.test_file: hash_file(self.test_file)
            }
        }
        with open(baseline_file, "w") as f:
            json.dump(baseline_data, f)
        
        mock_get_baseline.return_value = baseline_file
        mock_get_mount.return_value = self.test_dir
        
        result = save_consolidated_hash()
        
        self.assertIsNotNone(result)
        expected_file = os.path.join(self.test_dir, "consolidated_hashes.json")
        self.assertEqual(result, expected_file)
        self.assertTrue(os.path.exists(expected_file))
        
        # Verify file content
        with open(expected_file, "r") as f:
            consolidated_data = json.load(f)
        
        self.assertIn("master_hash", consolidated_data)
        self.assertIn("file_count", consolidated_data)
        self.assertIn("hash_list", consolidated_data)
    
    @patch('mjolnir.hashing.get_baseline_hash_file')
    @patch('mjolnir.config.get_usb_mount')
    @patch('mjolnir.hashing.log')
    def test_verify_consolidated_hash_success(self, mock_log, mock_get_mount, mock_get_baseline):
        """Test successful consolidated hash verification."""
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
        
        # Create consolidated hash file
        consolidated_file = os.path.join(self.test_dir, "consolidated_hashes.json")
        consolidated_data = {
            "master_hash": "test_master_hash",
            "file_count": 1,
            "hash_list": [f"{self.test_file}:{file_hash}"]
        }
        
        # Calculate correct master hash
        import hashlib
        master_hash_data = f"{self.test_file}:{file_hash}"
        correct_master_hash = hashlib.sha256(master_hash_data.encode()).hexdigest()
        consolidated_data["master_hash"] = correct_master_hash
        
        with open(consolidated_file, "w") as f:
            json.dump(consolidated_data, f)
        
        mock_get_baseline.return_value = baseline_file
        mock_get_mount.return_value = self.test_dir
        
        result = verify_consolidated_hash()
        
        self.assertTrue(result)
        mock_log.assert_any_call("✓ Consolidated hash verification PASSED")
    
    @patch('mjolnir.hashing.get_baseline_hash_file')
    @patch('mjolnir.hashing.log')
    def test_get_hash_summary_no_baseline(self, mock_log, mock_get_baseline):
        """Test hash summary when no baseline exists."""
        mock_get_baseline.return_value = os.path.join(self.test_dir, "nonexistent_baseline.json")
        
        result = get_hash_summary()
        
        self.assertFalse(result["baseline_exists"])
        self.assertEqual(result["file_count"], 0)
        self.assertEqual(result["categories"], {})
        self.assertIsNone(result["consolidated_hash"])
    
    @patch('mjolnir.hashing.get_baseline_hash_file')
    @patch('mjolnir.hashing.log')
    def test_get_hash_summary_with_baseline(self, mock_log, mock_get_baseline):
        """Test hash summary with existing baseline."""
        # Create baseline file
        baseline_file = os.path.join(self.test_dir, "baseline.json")
        baseline_data = {
            "TEST": {
                "/path/file1.txt": "hash1",
                "/path/file2.txt": "hash2"
            },
            "OTHER": {
                "/other/file3.txt": "hash3"
            }
        }
        with open(baseline_file, "w") as f:
            json.dump(baseline_data, f)
        
        mock_get_baseline.return_value = baseline_file
        
        result = get_hash_summary()
        
        self.assertTrue(result["baseline_exists"])
        self.assertEqual(result["file_count"], 3)
        self.assertEqual(result["categories"]["TEST"], 2)
        self.assertEqual(result["categories"]["OTHER"], 1)
        self.assertIsNotNone(result["consolidated_hash"])
        self.assertIsNotNone(result["last_updated"])


if __name__ == '__main__':
    unittest.main()
