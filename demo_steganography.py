#!/usr/bin/env python3
"""
MJOLNIR CyberChef Steganography Demo

This script demonstrates the steganography capabilities added to MJOLNIR.
It shows how to hide and extract messages from images and audio files.
"""

import os
import sys
import tempfile
import shutil
from PIL import Image
import numpy as np
import wave

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from cyberchef.steganography import (
    ImageSteganography,
    AudioSteganography, 
    TextEncoder,
    analyze_file
)


def create_demo_files(demo_dir):
    """Create demonstration image and audio files."""
    print("Creating demo files...")
    
    # Create a colorful gradient image
    width, height = 400, 300
    image_path = os.path.join(demo_dir, "demo_image.png")
    
    # Create RGB gradient
    img = Image.new('RGB', (width, height))
    pixels = []
    for y in range(height):
        for x in range(width):
            r = int(255 * x / width)
            g = int(255 * y / height)
            b = int(255 * (x + y) / (width + height))
            pixels.append((r, g, b))
    img.putdata(pixels)
    img.save(image_path)
    print(f"✓ Created demo image: {image_path}")
    
    # Create a simple tone audio file
    audio_path = os.path.join(demo_dir, "demo_audio.wav")
    sample_rate = 22050
    duration = 3  # seconds
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # Create a pleasant chord (C major)
    freq1, freq2, freq3 = 261.63, 329.63, 392.00  # C, E, G
    audio_data = (
        np.sin(2 * np.pi * freq1 * t) * 0.3 +
        np.sin(2 * np.pi * freq2 * t) * 0.3 +
        np.sin(2 * np.pi * freq3 * t) * 0.3
    ) * 10000  # Smaller amplitude to avoid overflow
    
    audio_data = audio_data.astype(np.int16)
    
    with wave.open(audio_path, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    print(f"✓ Created demo audio: {audio_path}")
    
    return image_path, audio_path


def demo_text_encoding():
    """Demonstrate text encoding utilities."""
    print("\n" + "="*50)
    print("TEXT ENCODING DEMONSTRATION")
    print("="*50)
    
    original_text = "Hello, this is a secret message!"
    print(f"Original text: {original_text}")
    
    # Text to binary
    binary = TextEncoder.text_to_binary(original_text)
    print(f"Binary representation: {binary[:50]}... (length: {len(binary)} bits)")
    
    # Binary back to text
    restored_text = TextEncoder.binary_to_text(binary)
    print(f"Restored text: {restored_text}")
    print(f"Round-trip successful: {original_text == restored_text}")
    
    # Base64 encoding
    base64_encoded = TextEncoder.encode_base64(original_text)
    print(f"Base64 encoded: {base64_encoded}")
    
    base64_decoded = TextEncoder.decode_base64(base64_encoded)
    print(f"Base64 decoded: {base64_decoded}")
    print(f"Base64 round-trip successful: {original_text == base64_decoded}")


def demo_image_steganography(image_path, demo_dir):
    """Demonstrate image steganography."""
    print("\n" + "="*50)
    print("IMAGE STEGANOGRAPHY DEMONSTRATION")
    print("="*50)
    
    # Analyze the image first
    analysis = analyze_file(image_path)
    print(f"Image analysis:")
    print(f"  File type: {analysis['file_type']}")
    print(f"  Steganography support: {analysis['steganography_support']}")
    print(f"  Capacity: {analysis['capacity_chars']:,} characters")
    print(f"  Capacity: {analysis['capacity_bits']:,} bits")
    print(f"  Method: {analysis['method']}")
    
    # Prepare message
    secret_message = """
    This is a secret message hidden inside an image using LSB steganography!
    
    MJOLNIR's CyberChef module can hide text in images by modifying the least
    significant bits of pixel values. This technique is virtually undetectable
    to the human eye but allows for secure communication.
    
    Features:
    - Supports PNG, JPEG, BMP formats
    - Uses LSB (Least Significant Bit) technique
    - Automatic message delimiting
    - Error handling for capacity limits
    
    Security level: HIGH 🔐
    """.strip()
    
    print(f"\nMessage to hide ({len(secret_message)} characters):")
    print(f'"{secret_message[:100]}..."')
    
    # Hide the message
    stego_image_path = os.path.join(demo_dir, "stego_image.png")
    print(f"\n🔒 Hiding message in image...")
    ImageSteganography.hide_text_in_image(image_path, secret_message, stego_image_path)
    print(f"✓ Message hidden successfully!")
    print(f"✓ Steganographic image saved: {stego_image_path}")
    
    # Extract the message
    print(f"\n🔍 Extracting message from steganographic image...")
    extracted_message = ImageSteganography.extract_text_from_image(stego_image_path)
    print(f"✓ Message extracted successfully!")
    print(f"\nExtracted message ({len(extracted_message)} characters):")
    print(f'"{extracted_message[:100]}..."')
    
    # Verify integrity
    if secret_message == extracted_message:
        print("✅ SUCCESS: Messages match perfectly!")
    else:
        print("❌ ERROR: Messages do not match!")
    
    # Show file sizes
    original_size = os.path.getsize(image_path)
    stego_size = os.path.getsize(stego_image_path)
    print(f"\nFile size comparison:")
    print(f"  Original: {original_size:,} bytes")
    print(f"  Steganographic: {stego_size:,} bytes")
    print(f"  Difference: {stego_size - original_size:,} bytes")


def demo_audio_steganography(audio_path, demo_dir):
    """Demonstrate audio steganography."""
    print("\n" + "="*50)
    print("AUDIO STEGANOGRAPHY DEMONSTRATION")
    print("="*50)
    
    # Analyze the audio file
    analysis = analyze_file(audio_path)
    print(f"Audio analysis:")
    print(f"  File type: {analysis['file_type']}")
    print(f"  Steganography support: {analysis['steganography_support']}")
    print(f"  Capacity: {analysis['capacity_chars']:,} characters")
    print(f"  Capacity: {analysis['capacity_bits']:,} bits")
    print(f"  Method: {analysis['method']}")
    
    # Prepare audio message
    audio_message = """
    CLASSIFIED AUDIO MESSAGE
    
    This message was hidden in an audio file using LSB steganography.
    The audio quality remains virtually unchanged while securely
    transmitting this text data.
    
    Mission: Operation CyberChef
    Status: ACTIVE
    Security: MAXIMUM
    
    End of message.
    """.strip()
    
    print(f"\nAudio message to hide ({len(audio_message)} characters):")
    print(f'"{audio_message[:100]}..."')
    
    # Hide the message
    stego_audio_path = os.path.join(demo_dir, "stego_audio.wav")
    print(f"\n🔒 Hiding message in audio...")
    AudioSteganography.hide_text_in_audio(audio_path, audio_message, stego_audio_path)
    print(f"✓ Message hidden successfully!")
    print(f"✓ Steganographic audio saved: {stego_audio_path}")
    
    # Extract the message
    print(f"\n🔍 Extracting message from steganographic audio...")
    extracted_audio_message = AudioSteganography.extract_text_from_audio(stego_audio_path)
    print(f"✓ Message extracted successfully!")
    print(f"\nExtracted audio message ({len(extracted_audio_message)} characters):")
    print(f'"{extracted_audio_message[:100]}..."')
    
    # Verify integrity
    if audio_message == extracted_audio_message:
        print("✅ SUCCESS: Audio messages match perfectly!")
    else:
        print("❌ ERROR: Audio messages do not match!")
    
    # Show file sizes
    original_size = os.path.getsize(audio_path)
    stego_size = os.path.getsize(stego_audio_path)
    print(f"\nFile size comparison:")
    print(f"  Original: {original_size:,} bytes")
    print(f"  Steganographic: {stego_size:,} bytes")
    print(f"  Difference: {stego_size - original_size:,} bytes")


def demo_capacity_analysis(demo_dir):
    """Demonstrate capacity analysis for different file types."""
    print("\n" + "="*50)
    print("CAPACITY ANALYSIS DEMONSTRATION")
    print("="*50)
    
    # Create files of different sizes
    sizes = [
        (100, 100, "small"),
        (400, 300, "medium"), 
        (800, 600, "large")
    ]
    
    print("Image capacity analysis:")
    for width, height, size_name in sizes:
        # Create test image
        img = Image.new('RGB', (width, height), color=(128, 128, 128))
        img_path = os.path.join(demo_dir, f"test_{size_name}.png")
        img.save(img_path)
        
        # Analyze capacity
        analysis = analyze_file(img_path)
        chars = analysis['capacity_chars']
        
        print(f"  {size_name.capitalize()} ({width}x{height}): {chars:,} characters")
        
        # Practical examples
        if chars > 1000000:
            print(f"    Could hide: entire books!")
        elif chars > 100000:
            print(f"    Could hide: long documents")
        elif chars > 10000:
            print(f"    Could hide: articles, reports")
        elif chars > 1000:
            print(f"    Could hide: messages, notes")
        else:
            print(f"    Could hide: short messages")


def main():
    """Main demonstration function."""
    print("🔨 MJOLNIR CYBERCHEF STEGANOGRAPHY DEMONSTRATION 🔨")
    print("="*60)
    print()
    print("This demo showcases the steganography capabilities added to MJOLNIR.")
    print("Features include:")
    print("  • LSB steganography for images (PNG, JPEG, BMP)")
    print("  • LSB steganography for audio (WAV)")
    print("  • Text encoding utilities")
    print("  • File capacity analysis")
    print("  • CyberChef-style interface")
    
    # Create temporary directory for demo
    demo_dir = tempfile.mkdtemp(prefix="mjolnir_stego_demo_")
    print(f"\nDemo files will be created in: {demo_dir}")
    
    try:
        # Create demo files
        image_path, audio_path = create_demo_files(demo_dir)
        
        # Run demonstrations
        demo_text_encoding()
        demo_image_steganography(image_path, demo_dir)
        demo_audio_steganography(audio_path, demo_dir)
        demo_capacity_analysis(demo_dir)
        
        print("\n" + "="*60)
        print("🎉 DEMONSTRATION COMPLETE! 🎉")
        print("="*60)
        print("\nAll steganography features are working correctly!")
        print(f"Demo files are available in: {demo_dir}")
        print("\nTo integrate with MJOLNIR GUI:")
        print("  1. Run the main MJOLNIR GUI")
        print("  2. Click 'CyberChef Steganography Tools'")
        print("  3. Use the tabbed interface for hiding/extracting messages")
        
        # List created files
        print(f"\nCreated demo files:")
        for filename in os.listdir(demo_dir):
            filepath = os.path.join(demo_dir, filename)
            size = os.path.getsize(filepath)
            print(f"  📁 {filename} ({size:,} bytes)")
        
        print(f"\n💡 Tip: You can use these files to test the GUI interface!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Offer to clean up
        response = input(f"\nClean up demo files in {demo_dir}? (y/N): ").strip().lower()
        if response == 'y':
            shutil.rmtree(demo_dir)
            print("✓ Demo files cleaned up")
        else:
            print(f"✓ Demo files preserved in {demo_dir}")


if __name__ == "__main__":
    main()