#!/usr/bin/env python3
"""
Audio to MP3 Converter
Converts WMA and DSS audio files to MP3 format in the RC participant directory structure.
"""

import os
import sys
import glob
import time
from pydub import AudioSegment

def print_header():
    """Print a fun header for the application"""
    print(" /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\")
    print("/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\")
    print("\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /")
    print(" \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/")
    print("")
    print("  EEEEE  BBBBB  RRRRR  L")
    print("  E      B   B  R   R  L")
    print("  EEEE   BBBB   RRRR   L")
    print("  E      B   B  R R    L")
    print("  EEEEE  BBBBB  R  R   LLLLL")
    print("")
    print(" /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\")
    print("/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\")
    print("\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /")
    print(" \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/")
    print("")
    print("=" * 60)
    print("    Audio to MP3 Converter")
    print("=" * 60)

def print_success(message):
    """Print a success message"""
    print(f"✓ {message}")

def print_info(message):
    """Print an info message"""
    print(f"ℹ  {message}")

def print_warning(message):
    """Print a warning message"""
    print(f"⚠  {message}")

def print_error(message):
    """Print an error message"""
    print(f"✗ {message}")

def print_progress(message):
    """Print a progress message"""
    print(f"→ {message}")

def print_separator():
    """Print a decorative separator"""
    print("=" * 60)

def print_mini_separator():
    """Print a mini decorative separator"""
    print("-" * 40)

def get_participant_name():
    """
    Prompt user for participant name and return the full directory path
    
    Returns:
        str: Full path to the participant directory
    """
    while True:
        print(f"\nEnter participant name: ", end="")
        participant_name = input().strip()
        if not participant_name:
            print_error("Participant name cannot be empty. Please try again.")
            continue
        
        # Construct the full path
        base_path = "/Users/armaanparikh/Documents/EBRL/RC"
        participant_path = os.path.join(base_path, participant_name)
        
        # Check if directory exists
        if not os.path.exists(participant_path):
            print_error(f"Directory not found: {participant_path}")
            print_info("Please check the participant name and try again.")
            continue
        
        print_success(f"Found participant directory: {participant_name}")
        return participant_path

def list_audio_files(directory):
    """
    List all WMA, DSS, and MP3 files in the directory
    
    Args:
        directory (str): Directory to search for audio files
    
    Returns:
        list: List of audio file paths
    """
    audio_files = []
    
    # Find all WMA, DSS, and MP3 files (case insensitive)
    wma_files = glob.glob(os.path.join(directory, "*.wma"))
    wma_files.extend(glob.glob(os.path.join(directory, "*.WMA")))
    dss_files = glob.glob(os.path.join(directory, "*.dss"))
    dss_files.extend(glob.glob(os.path.join(directory, "*.DSS")))
    mp3_files = glob.glob(os.path.join(directory, "*.mp3"))
    mp3_files.extend(glob.glob(os.path.join(directory, "*.MP3")))
    
    audio_files = wma_files + dss_files + mp3_files
    return sorted(audio_files)

def display_audio_files(audio_files):
    """
    Display numbered list of audio files with fun formatting
    
    Args:
        audio_files (list): List of audio file paths
    """
    if not audio_files:
        print_warning("No audio files (.wma, .dss, or .mp3) found in this directory.")
        return
    
    print(f"\nFound {len(audio_files)} audio file(s):")
    print_mini_separator()
    
    for i, file_path in enumerate(audio_files, 1):
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
        file_ext = os.path.splitext(filename)[1].lower()
        
        # Add file type indicator
        if file_ext == '.wma':
            type_indicator = "[WMA]"
        elif file_ext == '.dss':
            type_indicator = "[DSS]"
        elif file_ext == '.mp3':
            type_indicator = "[MP3]"
        else:
            type_indicator = "[FILE]"
        
        print(f"{i:2d}. {type_indicator} {filename} ({file_size:.1f} MB)")
    
    print_mini_separator()

def get_user_selection(audio_files, max_selections=3):
    """
    Get user selection for files to convert
    
    Args:
        audio_files (list): List of audio file paths
        max_selections (int): Maximum number of files user can select
    
    Returns:
        list: List of selected file paths
    """
    if not audio_files:
        return []
    
    selected_files = []
    
    print(f"\nSelect up to {max_selections} files to convert:")
    print("   Enter numbers separated by spaces, or 'all' for all files")
    print("   Note: Only WMA and DSS files will be converted to MP3. MP3 files will be skipped.")
    
    while True:
        try:
            print(f"\nEnter selection: ", end="")
            user_input = input().strip()
            
            if user_input.lower() == 'all':
                # Select all WMA and DSS files
                selected_files = [f for f in audio_files if f.lower().endswith(('.wma', '.dss'))]
                if not selected_files:
                    print_warning("No WMA or DSS files found to convert.")
                    return []
                print_success(f"Selected all {len(selected_files)} convertible files!")
                break
            
            # Parse user input
            selections = user_input.split()
            selected_indices = []
            
            for selection in selections:
                index = int(selection)
                if 1 <= index <= len(audio_files):
                    selected_indices.append(index - 1)  # Convert to 0-based index
                else:
                    print_error(f"Invalid selection: {selection}. Please enter numbers between 1 and {len(audio_files)}.")
                    selected_indices = []
                    break
            
            if selected_indices:
                if len(selected_indices) > max_selections:
                    print_error(f"Too many selections. Please select no more than {max_selections} files.")
                    continue
                
                selected_files = [audio_files[i] for i in selected_indices]
                print_success(f"Selected {len(selected_files)} file(s)!")
                break
                
        except ValueError:
            print_error("Invalid input. Please enter numbers separated by spaces, or 'all'.")
        except KeyboardInterrupt:
            print(f"\nOperation cancelled by user.")
            sys.exit(0)
    
    return selected_files

def show_conversion_progress(filename, current, total):
    """Show a fun progress indicator"""
    progress = (current / total) * 100
    bar_length = 30
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    print(f"\rConverting: {filename} [{bar}] {progress:.1f}% ({current}/{total})", end="", flush=True)

def convert_audio_to_mp3(input_file, bitrate="192k", current=1, total=1):
    """
    Convert a WMA or DSS file to MP3 format and save it in the same directory
    
    Args:
        input_file (str): Path to the input audio file
        bitrate (str): Bitrate for the output MP3 (default: "192k")
        current (int): Current file number for progress display
        total (int): Total number of files for progress display
    
    Returns:
        str: Path to the converted MP3 file, or None if conversion failed
    """
    try:
        # Check if input file exists
        if not os.path.exists(input_file):
            print_error(f"File {input_file} not found")
            return None
        
        # Check if input file is a supported format
        file_ext = input_file.lower()
        if not (file_ext.endswith('.wma') or file_ext.endswith('.dss')):
            print_info(f"{os.path.basename(input_file)} is not a WMA or DSS file. Skipping.")
            return None
        
        # Create output filename (same name but with .mp3 extension)
        output_file = os.path.splitext(input_file)[0] + '.mp3'
        
        # Check if output file already exists
        if os.path.exists(output_file):
            print_warning(f"{os.path.basename(output_file)} already exists. Skipping conversion.")
            return output_file
        
        filename = os.path.basename(input_file)
        print(f"\nConverting: {filename}")
        
        # Show progress animation
        for i in range(3):
            show_conversion_progress(filename, current, total)
            time.sleep(0.3)
        
        # Load the audio file
        print_progress("Loading audio file...")
        audio = AudioSegment.from_file(input_file)
        
        # Export as MP3
        print_progress("Converting to MP3...")
        audio.export(output_file, format="mp3", bitrate=bitrate)
        
        print(f"\nSuccessfully converted: {os.path.basename(output_file)}")
        return output_file
        
    except Exception as e:
        print(f"\nError converting {os.path.basename(input_file)}: {str(e)}")
        return None

def main():
    """
    Main function to handle the interactive audio to MP3 conversion
    """
    print_header()
    
    try:
        # Get participant directory
        participant_dir = get_participant_name()
        print_info(f"Working directory: {participant_dir}")
        
        # List audio files
        audio_files = list_audio_files(participant_dir)
        display_audio_files(audio_files)
        
        if not audio_files:
            print_warning("No audio files found. Exiting.")
            return
        
        # Get user selection
        selected_files = get_user_selection(audio_files, max_selections=3)
        
        if not selected_files:
            print_info("No files selected for conversion.")
            return
        
        # Filter to only WMA and DSS files
        convertible_files = [f for f in selected_files if f.lower().endswith(('.wma', '.dss'))]
        
        if not convertible_files:
            print_warning("No WMA or DSS files selected for conversion.")
            return
        
        print_separator()
        print(f"Starting conversion of {len(convertible_files)} file(s)...")
        print_separator()
        
        # Convert selected files
        converted_files = []
        failed_files = []
        
        for i, audio_file in enumerate(convertible_files, 1):
            result = convert_audio_to_mp3(audio_file, current=i, total=len(convertible_files))
            if result:
                converted_files.append(result)
            else:
                failed_files.append(audio_file)
        
        # Print summary
        print_separator()
        print("CONVERSION SUMMARY")
        print_separator()
        
        print_success(f"Successfully converted: {len(converted_files)} file(s)")
        if failed_files:
            print_error(f"Failed conversions: {len(failed_files)} file(s)")
        
        if converted_files:
            print(f"\nConverted files:")
            for file in converted_files:
                print(f"  ✓ {os.path.basename(file)}")
        
        if failed_files:
            print(f"\nFailed files:")
            for file in failed_files:
                print(f"  ✗ {os.path.basename(file)}")
        
        print_separator()
        print("Conversion process completed!")
        
    except KeyboardInterrupt:
        print(f"\nOperation cancelled by user.")
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 