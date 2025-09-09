"""
GUI components for CyberChef steganography tools.

Provides a user-friendly interface for steganography operations within MJOLNIR.
"""

import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os
import threading
from ..cyberchef.steganography import (
    ImageSteganography, 
    AudioSteganography, 
    TextEncoder,
    SteganographyError,
    analyze_file
)


class SteganographyGUI:
    """Main steganography GUI interface."""
    
    def __init__(self, parent):
        self.parent = parent
        self.window = None
    
    def show_window(self):
        """Display the steganography tools window."""
        if self.window is not None and self.window.winfo_exists():
            self.window.lift()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title("MJOLNIR CyberChef - Steganography Tools")
        self.window.geometry("600x500")
        self.window.resizable(True, True)
        
        # Make window modal
        self.window.transient(self.parent)
        self.window.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the GUI widgets."""
        # Main title
        title_label = tk.Label(
            self.window, 
            text="CyberChef Steganography Tools", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Image steganography tab
        self.image_frame = ttk.Frame(notebook)
        notebook.add(self.image_frame, text="Image Steganography")
        self._create_image_tab()
        
        # Audio steganography tab
        self.audio_frame = ttk.Frame(notebook)
        notebook.add(self.audio_frame, text="Audio Steganography")
        self._create_audio_tab()
        
        # Text encoding tab
        self.text_frame = ttk.Frame(notebook)
        notebook.add(self.text_frame, text="Text Encoding")
        self._create_text_tab()
        
        # File analysis tab
        self.analysis_frame = ttk.Frame(notebook)
        notebook.add(self.analysis_frame, text="File Analysis")
        self._create_analysis_tab()
        
        # Close button
        close_btn = tk.Button(
            self.window, 
            text="Close", 
            command=self.window.destroy,
            font=("Arial", 10)
        )
        close_btn.pack(pady=10)
    
    def _create_image_tab(self):
        """Create image steganography interface."""
        # Hide message section
        hide_frame = tk.LabelFrame(self.image_frame, text="Hide Message in Image")
        hide_frame.pack(fill="x", padx=10, pady=5)
        
        # Cover image selection
        cover_frame = tk.Frame(hide_frame)
        cover_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(cover_frame, text="Cover Image:").pack(side="left")
        self.cover_image_var = tk.StringVar()
        self.cover_entry = tk.Entry(cover_frame, textvariable=self.cover_image_var)
        self.cover_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        tk.Button(
            cover_frame, 
            text="Browse", 
            command=self._browse_cover_image
        ).pack(side="right")
        
        # Message input
        msg_frame = tk.Frame(hide_frame)
        msg_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        tk.Label(msg_frame, text="Message to Hide:").pack(anchor="w")
        self.message_text = tk.Text(msg_frame, height=4, wrap=tk.WORD)
        self.message_text.pack(fill="both", expand=True, pady=2)
        
        # Output path
        output_frame = tk.Frame(hide_frame)
        output_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(output_frame, text="Output Image:").pack(side="left")
        self.output_image_var = tk.StringVar()
        output_entry = tk.Entry(output_frame, textvariable=self.output_image_var)
        output_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        tk.Button(
            output_frame, 
            text="Browse", 
            command=self._browse_output_image
        ).pack(side="right")
        
        # Hide button
        tk.Button(
            hide_frame, 
            text="Hide Message", 
            command=self._hide_message_in_image,
            bg="lightgreen"
        ).pack(pady=5)
        
        # Extract message section
        extract_frame = tk.LabelFrame(self.image_frame, text="Extract Message from Image")
        extract_frame.pack(fill="x", padx=10, pady=5)
        
        # Source image selection
        source_frame = tk.Frame(extract_frame)
        source_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(source_frame, text="Source Image:").pack(side="left")
        self.source_image_var = tk.StringVar()
        source_entry = tk.Entry(source_frame, textvariable=self.source_image_var)
        source_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        tk.Button(
            source_frame, 
            text="Browse", 
            command=self._browse_source_image
        ).pack(side="right")
        
        # Extract button
        tk.Button(
            extract_frame, 
            text="Extract Message", 
            command=self._extract_message_from_image,
            bg="lightblue"
        ).pack(pady=5)
        
        # Extracted message display
        tk.Label(extract_frame, text="Extracted Message:").pack(anchor="w", padx=5)
        self.extracted_text = tk.Text(extract_frame, height=4, wrap=tk.WORD, state="disabled")
        self.extracted_text.pack(fill="both", expand=True, padx=5, pady=2)
    
    def _create_audio_tab(self):
        """Create audio steganography interface."""
        # Hide message section
        hide_frame = tk.LabelFrame(self.audio_frame, text="Hide Message in Audio")
        hide_frame.pack(fill="x", padx=10, pady=5)
        
        # Cover audio selection
        cover_frame = tk.Frame(hide_frame)
        cover_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(cover_frame, text="Cover Audio (.wav):").pack(side="left")
        self.cover_audio_var = tk.StringVar()
        cover_entry = tk.Entry(cover_frame, textvariable=self.cover_audio_var)
        cover_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        tk.Button(
            cover_frame, 
            text="Browse", 
            command=self._browse_cover_audio
        ).pack(side="right")
        
        # Message input
        msg_frame = tk.Frame(hide_frame)
        msg_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        tk.Label(msg_frame, text="Message to Hide:").pack(anchor="w")
        self.audio_message_text = tk.Text(msg_frame, height=4, wrap=tk.WORD)
        self.audio_message_text.pack(fill="both", expand=True, pady=2)
        
        # Output path
        output_frame = tk.Frame(hide_frame)
        output_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(output_frame, text="Output Audio:").pack(side="left")
        self.output_audio_var = tk.StringVar()
        output_entry = tk.Entry(output_frame, textvariable=self.output_audio_var)
        output_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        tk.Button(
            output_frame, 
            text="Browse", 
            command=self._browse_output_audio
        ).pack(side="right")
        
        # Hide button
        tk.Button(
            hide_frame, 
            text="Hide Message", 
            command=self._hide_message_in_audio,
            bg="lightgreen"
        ).pack(pady=5)
        
        # Extract message section
        extract_frame = tk.LabelFrame(self.audio_frame, text="Extract Message from Audio")
        extract_frame.pack(fill="x", padx=10, pady=5)
        
        # Source audio selection
        source_frame = tk.Frame(extract_frame)
        source_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(source_frame, text="Source Audio:").pack(side="left")
        self.source_audio_var = tk.StringVar()
        source_entry = tk.Entry(source_frame, textvariable=self.source_audio_var)
        source_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        tk.Button(
            source_frame, 
            text="Browse", 
            command=self._browse_source_audio
        ).pack(side="right")
        
        # Extract button
        tk.Button(
            extract_frame, 
            text="Extract Message", 
            command=self._extract_message_from_audio,
            bg="lightblue"
        ).pack(pady=5)
        
        # Extracted message display
        tk.Label(extract_frame, text="Extracted Message:").pack(anchor="w", padx=5)
        self.audio_extracted_text = tk.Text(extract_frame, height=4, wrap=tk.WORD, state="disabled")
        self.audio_extracted_text.pack(fill="both", expand=True, padx=5, pady=2)
    
    def _create_text_tab(self):
        """Create text encoding interface."""
        # Input section
        input_frame = tk.LabelFrame(self.text_frame, text="Input Text")
        input_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.input_text = tk.Text(input_frame, height=6, wrap=tk.WORD)
        self.input_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Encoding buttons
        button_frame = tk.Frame(self.text_frame)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Button(
            button_frame, 
            text="Text → Binary", 
            command=self._text_to_binary
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame, 
            text="Binary → Text", 
            command=self._binary_to_text
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame, 
            text="Text → Base64", 
            command=self._text_to_base64
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame, 
            text="Base64 → Text", 
            command=self._base64_to_text
        ).pack(side="left", padx=5)
        
        # Output section
        output_frame = tk.LabelFrame(self.text_frame, text="Output")
        output_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.output_text = tk.Text(output_frame, height=6, wrap=tk.WORD, state="disabled")
        self.output_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _create_analysis_tab(self):
        """Create file analysis interface."""
        # File selection
        file_frame = tk.Frame(self.analysis_frame)
        file_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(file_frame, text="File to Analyze:").pack(side="left")
        self.analysis_file_var = tk.StringVar()
        file_entry = tk.Entry(file_frame, textvariable=self.analysis_file_var)
        file_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        tk.Button(
            file_frame, 
            text="Browse", 
            command=self._browse_analysis_file
        ).pack(side="right")
        
        # Analyze button
        tk.Button(
            self.analysis_frame, 
            text="Analyze File", 
            command=self._analyze_file,
            bg="lightyellow"
        ).pack(pady=10)
        
        # Results display
        results_frame = tk.LabelFrame(self.analysis_frame, text="Analysis Results")
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.analysis_results = tk.Text(results_frame, wrap=tk.WORD, state="disabled")
        self.analysis_results.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Browse file methods
    def _browse_cover_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Cover Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.cover_image_var.set(file_path)
    
    def _browse_output_image(self):
        file_path = filedialog.asksaveasfilename(
            title="Save Output Image",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.output_image_var.set(file_path)
    
    def _browse_source_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Source Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.source_image_var.set(file_path)
    
    def _browse_cover_audio(self):
        file_path = filedialog.askopenfilename(
            title="Select Cover Audio",
            filetypes=[
                ("WAV files", "*.wav"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.cover_audio_var.set(file_path)
    
    def _browse_output_audio(self):
        file_path = filedialog.asksaveasfilename(
            title="Save Output Audio",
            defaultextension=".wav",
            filetypes=[
                ("WAV files", "*.wav"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.output_audio_var.set(file_path)
    
    def _browse_source_audio(self):
        file_path = filedialog.askopenfilename(
            title="Select Source Audio",
            filetypes=[
                ("WAV files", "*.wav"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.source_audio_var.set(file_path)
    
    def _browse_analysis_file(self):
        file_path = filedialog.askopenfilename(
            title="Select File to Analyze",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp"),
                ("Audio files", "*.wav"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.analysis_file_var.set(file_path)
    
    # Image steganography methods
    def _hide_message_in_image(self):
        cover_path = self.cover_image_var.get()
        message = self.message_text.get("1.0", tk.END).strip()
        output_path = self.output_image_var.get()
        
        if not cover_path or not message or not output_path:
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        try:
            ImageSteganography.hide_text_in_image(cover_path, message, output_path)
            messagebox.showinfo("Success", f"Message hidden successfully in {output_path}")
        except SteganographyError as e:
            messagebox.showerror("Steganography Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")
    
    def _extract_message_from_image(self):
        source_path = self.source_image_var.get()
        
        if not source_path:
            messagebox.showerror("Error", "Please select a source image")
            return
        
        try:
            message = ImageSteganography.extract_text_from_image(source_path)
            
            self.extracted_text.config(state="normal")
            self.extracted_text.delete("1.0", tk.END)
            self.extracted_text.insert("1.0", message)
            self.extracted_text.config(state="disabled")
            
            messagebox.showinfo("Success", "Message extracted successfully")
        except SteganographyError as e:
            messagebox.showerror("Steganography Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")
    
    # Audio steganography methods
    def _hide_message_in_audio(self):
        cover_path = self.cover_audio_var.get()
        message = self.audio_message_text.get("1.0", tk.END).strip()
        output_path = self.output_audio_var.get()
        
        if not cover_path or not message or not output_path:
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        try:
            AudioSteganography.hide_text_in_audio(cover_path, message, output_path)
            messagebox.showinfo("Success", f"Message hidden successfully in {output_path}")
        except SteganographyError as e:
            messagebox.showerror("Steganography Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")
    
    def _extract_message_from_audio(self):
        source_path = self.source_audio_var.get()
        
        if not source_path:
            messagebox.showerror("Error", "Please select a source audio file")
            return
        
        try:
            message = AudioSteganography.extract_text_from_audio(source_path)
            
            self.audio_extracted_text.config(state="normal")
            self.audio_extracted_text.delete("1.0", tk.END)
            self.audio_extracted_text.insert("1.0", message)
            self.audio_extracted_text.config(state="disabled")
            
            messagebox.showinfo("Success", "Message extracted successfully")
        except SteganographyError as e:
            messagebox.showerror("Steganography Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")
    
    # Text encoding methods
    def _text_to_binary(self):
        input_text = self.input_text.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showerror("Error", "Please enter text to convert")
            return
        
        try:
            binary = TextEncoder.text_to_binary(input_text)
            self._set_output_text(binary)
        except Exception as e:
            messagebox.showerror("Error", f"Conversion error: {e}")
    
    def _binary_to_text(self):
        input_text = self.input_text.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showerror("Error", "Please enter binary to convert")
            return
        
        try:
            text = TextEncoder.binary_to_text(input_text)
            self._set_output_text(text)
        except Exception as e:
            messagebox.showerror("Error", f"Conversion error: {e}")
    
    def _text_to_base64(self):
        input_text = self.input_text.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showerror("Error", "Please enter text to encode")
            return
        
        try:
            base64_text = TextEncoder.encode_base64(input_text)
            self._set_output_text(base64_text)
        except Exception as e:
            messagebox.showerror("Error", f"Encoding error: {e}")
    
    def _base64_to_text(self):
        input_text = self.input_text.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showerror("Error", "Please enter base64 to decode")
            return
        
        try:
            text = TextEncoder.decode_base64(input_text)
            self._set_output_text(text)
        except Exception as e:
            messagebox.showerror("Error", f"Decoding error: {e}")
    
    def _set_output_text(self, text):
        """Set text in output field."""
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", text)
        self.output_text.config(state="disabled")
    
    # File analysis method
    def _analyze_file(self):
        file_path = self.analysis_file_var.get()
        
        if not file_path:
            messagebox.showerror("Error", "Please select a file to analyze")
            return
        
        try:
            analysis = analyze_file(file_path)
            
            # Format results
            results = f"File Analysis Results\n"
            results += f"{'='*30}\n\n"
            results += f"File Path: {analysis['file_path']}\n"
            results += f"File Type: {analysis['file_type']}\n"
            results += f"File Size: {analysis['file_size']:,} bytes\n\n"
            
            if analysis['steganography_support']:
                results += f"Steganography Support: ✓ YES\n"
                results += f"Method: {analysis.get('method', 'Unknown')}\n"
                results += f"Capacity: {analysis['capacity_bits']:,} bits\n"
                results += f"Capacity: {analysis['capacity_chars']:,} characters\n"
                
                # Calculate some practical examples
                capacity_mb = analysis['capacity_bits'] / (8 * 1024 * 1024)
                results += f"Capacity: {capacity_mb:.3f} MB of data\n"
                
                # Examples
                results += f"\nPractical Examples:\n"
                results += f"- Could hide up to {analysis['capacity_chars']//100} small paragraphs\n"
                results += f"- Could hide a {analysis['capacity_chars']//1000}KB text file\n"
                
                if analysis['capacity_chars'] > 1000000:
                    results += f"- Could hide a small novel!\n"
                elif analysis['capacity_chars'] > 100000:
                    results += f"- Could hide a long document\n"
                elif analysis['capacity_chars'] > 10000:
                    results += f"- Could hide a moderate document\n"
                else:
                    results += f"- Could hide a short message\n"
            else:
                results += f"Steganography Support: ✗ NO\n"
                results += f"Supported formats: PNG, JPEG, BMP (images), WAV (audio)\n"
            
            if 'error' in analysis:
                results += f"\nError: {analysis['error']}\n"
            
            # Display results
            self.analysis_results.config(state="normal")
            self.analysis_results.delete("1.0", tk.END)
            self.analysis_results.insert("1.0", results)
            self.analysis_results.config(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Error", f"Analysis error: {e}")