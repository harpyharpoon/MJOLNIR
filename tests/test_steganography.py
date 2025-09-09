import unittest
import tempfile
import os
import shutil
import numpy as np
from PIL import Image
import wave
import sys

# Add the parent directory to the path to import cyberchef modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cyberchef.steganography import (
    ImageSteganography, 
    AudioSteganography, 
    TextEncoder, 
    SteganographyError,
    analyze_file
)


class TestSteganography(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment before each test."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create test image
        self.test_image = os.path.join(self.test_dir, "test_image.png")
        img_array = np.random.randint(0, 128, (100, 100, 3), dtype=np.uint8)  # Use smaller values
        img = Image.fromarray(img_array)
        img.save(self.test_image)
        
        # Create test audio
        self.test_audio = os.path.join(self.test_dir, "test_audio.wav")
        sample_rate = 8000  # Smaller for faster tests
        duration = 0.5
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        frequency = 440
        audio_data = (np.sin(2 * np.pi * frequency * t) * 8000).astype(np.int16)  # Smaller amplitude
        
        with wave.open(self.test_audio, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
    
    def tearDown(self):
        """Clean up test environment after each test."""
        shutil.rmtree(self.test_dir)
    
    def test_text_encoder_binary(self):
        """Test text to binary conversion."""
        text = "Hello"
        binary = TextEncoder.text_to_binary(text)
        self.assertEqual(len(binary), len(text) * 8)
        
        # Test round trip
        back_to_text = TextEncoder.binary_to_text(binary)
        self.assertEqual(text, back_to_text)
    
    def test_text_encoder_base64(self):
        """Test base64 encoding/decoding."""
        text = "Hello World!"
        encoded = TextEncoder.encode_base64(text)
        decoded = TextEncoder.decode_base64(encoded)
        self.assertEqual(text, decoded)
    
    def test_image_steganography_round_trip(self):
        """Test hiding and extracting text from image."""
        message = "Secret message"
        output_image = os.path.join(self.test_dir, "stego_image.png")
        
        # Hide message
        ImageSteganography.hide_text_in_image(self.test_image, message, output_image)
        self.assertTrue(os.path.exists(output_image))
        
        # Extract message
        extracted = ImageSteganography.extract_text_from_image(output_image)
        self.assertEqual(message, extracted)
    
    def test_image_capacity(self):
        """Test image capacity calculation."""
        capacity = ImageSteganography.get_image_capacity(self.test_image)
        self.assertGreater(capacity, 0)
        # Should be width * height * channels
        self.assertEqual(capacity, 100 * 100 * 3)
    
    def test_audio_steganography_round_trip(self):
        """Test hiding and extracting text from audio."""
        message = "Audio secret"
        output_audio = os.path.join(self.test_dir, "stego_audio.wav")
        
        # Hide message
        AudioSteganography.hide_text_in_audio(self.test_audio, message, output_audio)
        self.assertTrue(os.path.exists(output_audio))
        
        # Extract message
        extracted = AudioSteganography.extract_text_from_audio(output_audio)
        self.assertEqual(message, extracted)
    
    def test_audio_capacity(self):
        """Test audio capacity calculation."""
        capacity = AudioSteganography.get_audio_capacity(self.test_audio)
        self.assertGreater(capacity, 0)
    
    def test_message_too_long_image(self):
        """Test error when message is too long for image."""
        # Create very long message
        long_message = "x" * 10000
        output_image = os.path.join(self.test_dir, "stego_image.png")
        
        with self.assertRaises(SteganographyError):
            ImageSteganography.hide_text_in_image(self.test_image, long_message, output_image)
    
    def test_message_too_long_audio(self):
        """Test error when message is too long for audio."""
        # Create very long message
        long_message = "x" * 5000
        output_audio = os.path.join(self.test_dir, "stego_audio.wav")
        
        with self.assertRaises(SteganographyError):
            AudioSteganography.hide_text_in_audio(self.test_audio, long_message, output_audio)
    
    def test_extract_from_clean_image(self):
        """Test extracting from image without hidden message."""
        with self.assertRaises(SteganographyError):
            ImageSteganography.extract_text_from_image(self.test_image)
    
    def test_extract_from_clean_audio(self):
        """Test extracting from audio without hidden message."""
        with self.assertRaises(SteganographyError):
            AudioSteganography.extract_text_from_audio(self.test_audio)
    
    def test_analyze_image_file(self):
        """Test file analysis for image."""
        analysis = analyze_file(self.test_image)
        
        self.assertTrue(analysis['steganography_support'])
        self.assertEqual(analysis['file_type'], '.png')
        self.assertGreater(analysis['capacity_bits'], 0)
        self.assertEqual(analysis['method'], 'LSB Image Steganography')
    
    def test_analyze_audio_file(self):
        """Test file analysis for audio."""
        analysis = analyze_file(self.test_audio)
        
        self.assertTrue(analysis['steganography_support'])
        self.assertEqual(analysis['file_type'], '.wav')
        self.assertGreater(analysis['capacity_bits'], 0)
        self.assertEqual(analysis['method'], 'LSB Audio Steganography')
    
    def test_analyze_unsupported_file(self):
        """Test file analysis for unsupported file type."""
        text_file = os.path.join(self.test_dir, "test.txt")
        with open(text_file, 'w') as f:
            f.write("test content")
        
        analysis = analyze_file(text_file)
        self.assertFalse(analysis['steganography_support'])
        self.assertEqual(analysis['file_type'], '.txt')
    
    def test_nonexistent_file(self):
        """Test handling of nonexistent files."""
        fake_file = os.path.join(self.test_dir, "nonexistent.png")
        
        with self.assertRaises(SteganographyError):
            ImageSteganography.hide_text_in_image(fake_file, "test", "/tmp/out.png")
        
        with self.assertRaises(SteganographyError):
            ImageSteganography.extract_text_from_image(fake_file)


if __name__ == '__main__':
    unittest.main()