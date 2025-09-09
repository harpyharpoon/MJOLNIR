# CyberChef Steganography Module for MJOLNIR

This module adds comprehensive steganography capabilities to MJOLNIR, inspired by the popular CyberChef tool. It provides easy-to-use interfaces for hiding and extracting data from images and audio files.

## Features

### 🖼️ Image Steganography
- **LSB (Least Significant Bit) technique** for images
- **Supported formats**: PNG, JPEG, BMP
- **Invisible to human eye** - minimal impact on image quality
- **Automatic capacity calculation** - knows how much data can be hidden
- **Error handling** - prevents data corruption and capacity overflow

### 🎵 Audio Steganography  
- **LSB technique** for audio files
- **Supported formats**: WAV (16-bit)
- **Maintains audio quality** - changes are inaudible
- **High capacity** - can hide substantial amounts of text
- **Preserves file size** - steganographic files are same size as originals

### 🔤 Text Encoding Utilities
- **Binary conversion** - text to/from binary representation
- **Base64 encoding/decoding** - for additional obfuscation
- **Unicode support** - handles international characters
- **Error checking** - validates data integrity

### 📊 File Analysis
- **Capacity analysis** - calculates maximum hidden data capacity
- **Format detection** - automatically identifies supported file types
- **Usage examples** - shows practical capacity in real-world terms
- **Performance metrics** - file size impact analysis

## Installation

The module requires the following Python packages:
```bash
pip install Pillow numpy
```

## Quick Start

### Basic Image Steganography
```python
from cyberchef.steganography import ImageSteganography

# Hide message
ImageSteganography.hide_text_in_image(
    cover_image="photo.png",
    message="Secret message!",
    output_image="stego_photo.png"
)

# Extract message
message = ImageSteganography.extract_text_from_image("stego_photo.png")
print(message)  # Output: "Secret message!"
```

### Basic Audio Steganography
```python
from cyberchef.steganography import AudioSteganography

# Hide message
AudioSteganography.hide_text_in_audio(
    audio_path="audio.wav",
    message="Secret audio message!",
    output_path="stego_audio.wav"
)

# Extract message
message = AudioSteganography.extract_text_from_audio("stego_audio.wav")
print(message)  # Output: "Secret audio message!"
```

### File Analysis
```python
from cyberchef.steganography import analyze_file

analysis = analyze_file("image.png")
print(f"Can hide {analysis['capacity_chars']} characters")
print(f"Steganography support: {analysis['steganography_support']}")
```

### Text Encoding
```python
from cyberchef.steganography import TextEncoder

# Convert to binary
binary = TextEncoder.text_to_binary("Hello World")
print(binary)  # Output: binary representation

# Convert back to text
text = TextEncoder.binary_to_text(binary)
print(text)  # Output: "Hello World"

# Base64 encoding
encoded = TextEncoder.encode_base64("Secret")
decoded = TextEncoder.decode_base64(encoded)
```

## GUI Interface

The module includes a comprehensive graphical interface accessible through the main MJOLNIR GUI:

1. **Launch MJOLNIR** GUI
2. **Click** "CyberChef Steganography Tools"
3. **Use tabs** for different operations:
   - **Image Steganography** - Hide/extract from images
   - **Audio Steganography** - Hide/extract from audio
   - **Text Encoding** - Convert between formats
   - **File Analysis** - Analyze capacity and properties

### GUI Features
- **File browsers** - Easy file selection
- **Text areas** - Large message input/output
- **Real-time feedback** - Success/error notifications
- **Capacity checking** - Prevents overflow errors
- **Multiple formats** - Support for various file types

## Technical Details

### LSB Steganography Algorithm

The module uses **Least Significant Bit (LSB)** steganography:

1. **Message Preparation**:
   - Convert text to binary representation
   - Add delimiter to mark message end
   - Check capacity constraints

2. **Data Hiding**:
   - Modify LSB of each pixel/sample
   - Preserve visual/audio quality
   - Maintain file structure integrity

3. **Data Extraction**:
   - Read LSBs sequentially
   - Detect delimiter to find message end
   - Convert binary back to text

### Security Considerations

- **Invisible Changes**: Modifications are imperceptible to human senses
- **File Integrity**: Original file structure is preserved
- **Capacity Limits**: Automatic prevention of data overflow
- **Error Detection**: Validates message integrity during extraction

### Performance

- **Image Processing**: Fast pixel manipulation using NumPy
- **Audio Processing**: Efficient sample-level operations
- **Memory Efficient**: Processes large files without excessive RAM usage
- **Format Support**: Optimized for common file formats

## Capacity Guidelines

### Image Files
- **100x100 pixels**: ~3,750 characters
- **400x300 pixels**: ~45,000 characters (small document)
- **800x600 pixels**: ~180,000 characters (long document)
- **1920x1080 pixels**: ~777,600 characters (book chapter)

### Audio Files
- **1 minute @ 44.1kHz**: ~2.6M characters (entire book!)
- **10 seconds @ 22kHz**: ~220,000 characters (long article)
- **Quality vs Capacity**: Higher sample rates = more capacity

## Error Handling

The module includes comprehensive error handling:

- **File Not Found**: Clear error messages for missing files
- **Capacity Overflow**: Prevents data loss from oversized messages
- **Format Errors**: Validates file formats before processing
- **Extraction Failures**: Detects corrupted or missing hidden data
- **Permission Errors**: Handles file access issues gracefully

## Examples and Demos

Run the included demonstration script:
```bash
python demo_steganography.py
```

This showcases:
- Text encoding/decoding
- Image steganography round-trip
- Audio steganography round-trip  
- Capacity analysis for different file sizes
- File creation and manipulation examples

## Integration with MJOLNIR

The steganography module integrates seamlessly with MJOLNIR's security features:

- **USB Security**: Hide authentication data in images/audio
- **Backup Protection**: Embed verification data in backups
- **Covert Communication**: Secure message transmission
- **Data Integrity**: Hidden checksums and metadata
- **Security Auditing**: Steganographic evidence trails

## Future Enhancements

Planned features for future versions:

- **FFT-based steganography** - Frequency domain hiding
- **Video steganography** - Hide data in video files
- **Advanced encryption** - Encrypt before hiding
- **Batch processing** - Process multiple files at once
- **Compression support** - Handle compressed formats
- **Steganographic analysis** - Detect hidden data in files

## Troubleshooting

### Common Issues

1. **"Module not found" errors**:
   ```bash
   pip install Pillow numpy
   ```

2. **"Capacity exceeded" errors**:
   - Use larger cover files
   - Compress your message
   - Check capacity with `analyze_file()`

3. **"No hidden message found"**:
   - Verify file hasn't been recompressed
   - Ensure you're using the correct stego file
   - Check for file corruption

4. **GUI not working**:
   - Ensure tkinter is installed
   - Check Python GUI capabilities
   - Try command-line interface instead

### Performance Tips

- **Use PNG format** for images (lossless compression)
- **Higher bit-depth audio** = more capacity
- **Larger files** = more hiding space
- **Batch operations** for multiple files

## Contributing

Contributions welcome! Areas for improvement:
- Additional file format support
- Advanced steganographic techniques
- Performance optimizations
- Security enhancements
- User interface improvements

## License

This module is part of the MJOLNIR project and follows the same licensing terms.