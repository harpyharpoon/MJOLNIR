"""
Steganography implementations for MJOLNIR CyberChef module.

Provides various steganography techniques for hiding data in images and audio files.
"""

import os
import struct
import numpy as np
from PIL import Image
from typing import Optional, Tuple, Union
import base64
import wave


class SteganographyError(Exception):
    """Custom exception for steganography operations."""
    pass


class TextEncoder:
    """Utility class for text encoding/decoding operations."""
    
    @staticmethod
    def text_to_binary(text: str) -> str:
        """Convert text to binary representation."""
        return ''.join(format(ord(char), '08b') for char in text)
    
    @staticmethod
    def binary_to_text(binary: str) -> str:
        """Convert binary representation back to text."""
        # Remove any trailing bits that don't form complete bytes
        binary = binary[:len(binary) // 8 * 8]
        
        if len(binary) % 8 != 0:
            raise SteganographyError("Binary string length must be multiple of 8")
        
        text = ''
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            text += chr(int(byte, 2))
        return text
    
    @staticmethod
    def encode_base64(data: str) -> str:
        """Encode text as base64."""
        return base64.b64encode(data.encode()).decode()
    
    @staticmethod
    def decode_base64(data: str) -> str:
        """Decode base64 text."""
        return base64.b64decode(data.encode()).decode()


class ImageSteganography:
    """LSB steganography for images."""
    
    DELIMITER = "1111111111111110"  # Binary delimiter to mark end of message
    
    @classmethod
    def hide_text_in_image(cls, image_path: str, message: str, output_path: str) -> None:
        """
        Hide text message in image using LSB steganography.
        
        Args:
            image_path: Path to cover image
            message: Text message to hide
            output_path: Path for output image with hidden message
        """
        try:
            # Open image and convert to RGB
            img = Image.open(image_path).convert('RGB')
            width, height = img.size
            
            # Convert message to binary and add delimiter
            binary_message = TextEncoder.text_to_binary(message) + cls.DELIMITER
            
            # Check if image is large enough
            max_capacity = width * height * 3  # 3 color channels
            if len(binary_message) > max_capacity:
                raise SteganographyError(
                    f"Message too long for image. Max capacity: {max_capacity} bits, "
                    f"message length: {len(binary_message)} bits"
                )
            
            # Convert image to numpy array for easier manipulation
            img_array = np.array(img)
            
            # Flatten array to work with 1D indexing
            flat_array = img_array.flatten()
            
            # Hide message in LSBs
            for i, bit in enumerate(binary_message):
                # Modify LSB of each color value
                flat_array[i] = (flat_array[i] & 0xFE) | int(bit)
            
            # Reshape back to original dimensions
            modified_array = flat_array.reshape(img_array.shape)
            
            # Save modified image
            modified_img = Image.fromarray(modified_array.astype('uint8'), 'RGB')
            modified_img.save(output_path, 'PNG')
            
        except Exception as e:
            raise SteganographyError(f"Error hiding text in image: {e}")
    
    @classmethod
    def extract_text_from_image(cls, image_path: str) -> str:
        """
        Extract hidden text from image using LSB steganography.
        
        Args:
            image_path: Path to image with hidden message
            
        Returns:
            Extracted text message
        """
        try:
            # Open image and convert to RGB
            img = Image.open(image_path).convert('RGB')
            
            # Convert to numpy array and flatten
            img_array = np.array(img)
            flat_array = img_array.flatten()
            
            # Extract LSBs
            binary_message = ''
            for pixel_value in flat_array:
                binary_message += str(pixel_value & 1)
                
                # Check for delimiter
                if binary_message.endswith(cls.DELIMITER):
                    # Remove delimiter and convert to text
                    binary_message = binary_message[:-len(cls.DELIMITER)]
                    return TextEncoder.binary_to_text(binary_message)
            
            raise SteganographyError("No hidden message found or delimiter not detected")
            
        except Exception as e:
            raise SteganographyError(f"Error extracting text from image: {e}")
    
    @classmethod
    def get_image_capacity(cls, image_path: str) -> int:
        """
        Get maximum message capacity for an image in bits.
        
        Args:
            image_path: Path to image
            
        Returns:
            Maximum capacity in bits
        """
        try:
            img = Image.open(image_path)
            width, height = img.size
            if img.mode == 'RGB':
                return width * height * 3
            elif img.mode == 'RGBA':
                return width * height * 4
            else:
                return width * height
        except Exception as e:
            raise SteganographyError(f"Error calculating image capacity: {e}")


class AudioSteganography:
    """LSB steganography for audio files."""
    
    DELIMITER = "1111111111111110"  # Binary delimiter to mark end of message
    
    @classmethod
    def hide_text_in_audio(cls, audio_path: str, message: str, output_path: str) -> None:
        """
        Hide text message in audio file using LSB steganography.
        
        Args:
            audio_path: Path to cover audio file (WAV)
            message: Text message to hide
            output_path: Path for output audio file with hidden message
        """
        try:
            # Open audio file
            with wave.open(audio_path, 'rb') as audio:
                frames = audio.readframes(-1)
                params = audio.getparams()
                
                # Convert to numpy array
                if params.sampwidth == 2:  # 16-bit
                    audio_data = np.frombuffer(frames, dtype=np.int16).copy()
                else:
                    raise SteganographyError("Only 16-bit WAV files are supported")
                
                # Convert message to binary and add delimiter
                binary_message = TextEncoder.text_to_binary(message) + cls.DELIMITER
                
                # Check capacity
                if len(binary_message) > len(audio_data):
                    raise SteganographyError(
                        f"Message too long for audio file. Max capacity: {len(audio_data)} bits, "
                        f"message length: {len(binary_message)} bits"
                    )
                
                # Hide message in LSBs
                for i, bit in enumerate(binary_message):
                    # Clear LSB and set new bit, handle negative values properly
                    current_val = audio_data[i]
                    # For signed 16-bit integers, we need to handle the sign bit carefully
                    new_val = (current_val & -2) | int(bit)  # -2 is 0xFFFE in two's complement
                    audio_data[i] = new_val
                
                # Write modified audio
                with wave.open(output_path, 'wb') as output_audio:
                    output_audio.setparams(params)
                    output_audio.writeframes(audio_data.tobytes())
                    
        except Exception as e:
            raise SteganographyError(f"Error hiding text in audio: {e}")
    
    @classmethod
    def extract_text_from_audio(cls, audio_path: str) -> str:
        """
        Extract hidden text from audio file using LSB steganography.
        
        Args:
            audio_path: Path to audio file with hidden message
            
        Returns:
            Extracted text message
        """
        try:
            # Open audio file
            with wave.open(audio_path, 'rb') as audio:
                frames = audio.readframes(-1)
                params = audio.getparams()
                
                # Convert to numpy array
                if params.sampwidth == 2:  # 16-bit
                    audio_data = np.frombuffer(frames, dtype=np.int16)
                else:
                    raise SteganographyError("Only 16-bit WAV files are supported")
                
                # Extract LSBs
                binary_message = ''
                for sample in audio_data:
                    binary_message += str(sample & 1)
                    
                    # Check for delimiter
                    if binary_message.endswith(cls.DELIMITER):
                        # Remove delimiter and convert to text
                        binary_message = binary_message[:-len(cls.DELIMITER)]
                        return TextEncoder.binary_to_text(binary_message)
                
                raise SteganographyError("No hidden message found or delimiter not detected")
                
        except Exception as e:
            raise SteganographyError(f"Error extracting text from audio: {e}")
    
    @classmethod
    def get_audio_capacity(cls, audio_path: str) -> int:
        """
        Get maximum message capacity for an audio file in bits.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Maximum capacity in bits
        """
        try:
            with wave.open(audio_path, 'rb') as audio:
                frames = audio.readframes(-1)
                params = audio.getparams()
                
                if params.sampwidth == 2:  # 16-bit
                    audio_data = np.frombuffer(frames, dtype=np.int16)
                    return len(audio_data)
                else:
                    raise SteganographyError("Only 16-bit WAV files are supported")
                    
        except Exception as e:
            raise SteganographyError(f"Error calculating audio capacity: {e}")


class FFTSteganography:
    """FFT-based steganography for audio files."""
    
    @classmethod
    def hide_text_in_fft(cls, audio_path: str, message: str, output_path: str, 
                        frequency_range: Tuple[int, int] = (1000, 2000)) -> None:
        """
        Hide text in audio using FFT frequency domain manipulation.
        
        Args:
            audio_path: Path to cover audio file
            message: Text message to hide
            output_path: Path for output audio file
            frequency_range: Frequency range to use for hiding (Hz)
        """
        try:
            with wave.open(audio_path, 'rb') as audio:
                frames = audio.readframes(-1)
                params = audio.getparams()
                
                if params.sampwidth != 2:
                    raise SteganographyError("Only 16-bit WAV files are supported")
                
                # Convert to numpy array
                audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
                sample_rate = params.framerate
                
                # Convert message to binary
                binary_message = TextEncoder.text_to_binary(message)
                
                # Apply FFT
                fft_data = np.fft.fft(audio_data)
                freqs = np.fft.fftfreq(len(audio_data), 1/sample_rate)
                
                # Find frequency indices for hiding
                min_freq, max_freq = frequency_range
                freq_mask = (np.abs(freqs) >= min_freq) & (np.abs(freqs) <= max_freq)
                available_indices = np.where(freq_mask)[0]
                
                if len(binary_message) > len(available_indices):
                    raise SteganographyError(
                        f"Message too long for frequency range. Available: {len(available_indices)}, "
                        f"needed: {len(binary_message)}"
                    )
                
                # Modify phase to encode message
                for i, bit in enumerate(binary_message):
                    idx = available_indices[i]
                    if bit == '1':
                        # Modify phase slightly
                        magnitude = np.abs(fft_data[idx])
                        phase = np.angle(fft_data[idx])
                        phase += np.pi / 4  # Add phase shift
                        fft_data[idx] = magnitude * np.exp(1j * phase)
                
                # Convert back to time domain
                modified_audio = np.fft.ifft(fft_data).real.astype(np.int16)
                
                # Write modified audio
                with wave.open(output_path, 'wb') as output_audio:
                    output_audio.setparams(params)
                    output_audio.writeframes(modified_audio.tobytes())
                    
        except Exception as e:
            raise SteganographyError(f"Error hiding text using FFT: {e}")


# Utility functions for the cyberchef module
def analyze_file(file_path: str) -> dict:
    """
    Analyze a file to determine its steganography capacity and properties.
    
    Args:
        file_path: Path to file to analyze
        
    Returns:
        Dictionary with file analysis results
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    analysis = {
        'file_path': file_path,
        'file_type': file_ext,
        'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
        'steganography_support': False,
        'capacity_bits': 0,
        'capacity_chars': 0
    }
    
    try:
        if file_ext in ['.png', '.jpg', '.jpeg', '.bmp']:
            analysis['steganography_support'] = True
            analysis['capacity_bits'] = ImageSteganography.get_image_capacity(file_path)
            analysis['capacity_chars'] = analysis['capacity_bits'] // 8
            analysis['method'] = 'LSB Image Steganography'
            
        elif file_ext == '.wav':
            analysis['steganography_support'] = True
            analysis['capacity_bits'] = AudioSteganography.get_audio_capacity(file_path)
            analysis['capacity_chars'] = analysis['capacity_bits'] // 8
            analysis['method'] = 'LSB Audio Steganography'
            
    except Exception as e:
        analysis['error'] = str(e)
    
    return analysis